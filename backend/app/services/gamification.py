"""
Gamification service: the XP ledger, levels, streaks, daily goal, badges and leaderboard.

See GAMIFICATION.md at the repository root; every constant and pure rule lives in
app/services/gamification_rules.py.

Design notes
  * Server-authoritative and idempotent: awarding means "insert an xp_events row; if the unique
    (user_id, kind, ref_key) constraint rejects it, it was already awarded". The insert runs in a
    SAVEPOINT so a lost race only rolls back that one insert, and the cached profile.xp_total is
    bumped with an SQL expression (`xp_total = xp_total + :amount`) in the same transaction.
  * Every record_* call locks the learner's profile row (SELECT ... FOR UPDATE on PostgreSQL, a
    no-op on SQLite) so concurrent requests from one learner are serialised and cannot double-count
    streaks, daily XP or quiz deltas.
  * record_* functions commit their own transaction and always return a RewardSummary.
  * Dates are the learner's local dates (see local_today); datetimes are timezone-aware UTC in
    Python, and naive datetimes coming back from SQLite are normalised before use.
"""
import math
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.gamification import GamificationProfile, UserBadge, XPEvent
from app.models.progress import CodeSubmission, LessonProgress, QuizAttempt, SubmissionStatus
from app.models.user import User
from app.schemas.gamification import (
    BadgeInfo,
    BadgeProgress,
    DailyInfo,
    GamificationSummary,
    LeaderboardEntry,
    LeaderboardMe,
    LeaderboardResponse,
    RecentEvent,
    RewardEvent,
    RewardSummary,
    SettingsUpdate,
    StreakInfo,
    WeeklyPoint,
)
from app.schemas.module import ModuleDetail
from app.services.gamification_rules import (
    BADGES,
    BADGES_BY_ID,
    DEFAULT_DAILY_GOAL,
    GENERATED_MODULE_PREFIX,
    KIND_COMEBACK,
    KIND_DAILY_GOAL,
    KIND_FIRST_TRY,
    KIND_LESSON,
    KIND_MODULE_COMPLETE,
    KIND_PROBLEM,
    KIND_QUIZ,
    KIND_QUIZ_PERFECT,
    KIND_STREAK_MILESTONE,
    LESSON_MIN_GAP,
    MODULE_QUIZ_PASS_PCT,
    QUIZ_RETRY_COOLDOWN,
    STREAK_MILESTONES,
    TZ_CHANGE_COOLDOWN,
    XP_DAILY_GOAL,
    XP_FIRST_TRY,
    XP_LESSON,
    XP_MODULE_COMPLETE,
    XP_QUIZ_PERFECT,
    BadgeDef,
    StreakResult,
    anonymise_name,
    compute_streak,
    event_label,
    level_for_xp,
    level_progress,
    normalise_difficulty,
    problem_xp,
    quiz_target_xp,
    streak_milestone_xp,
)

LEADERBOARD_SIZE = 10
LEADERBOARD_DAYS = 7
RECENT_BADGES = 4
RECENT_EVENTS = 8
_MAX_REF_LEN = 255  # xp_events.ref_key column width
_MAX_TZ_OFFSET = 840

_UTC = timezone.utc

# Ledger kinds whose rows feed the badge statistics.
_STAT_KINDS = (
    KIND_LESSON, KIND_QUIZ, KIND_QUIZ_PERFECT, KIND_PROBLEM, KIND_FIRST_TRY,
    KIND_MODULE_COMPLETE, KIND_DAILY_GOAL, KIND_COMEBACK,
)


# --------------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------------


def _utcnow() -> datetime:
    return datetime.now(_UTC)


def _aware(value: datetime) -> datetime:
    """SQLite hands back naive datetimes; everything we store is UTC."""
    return value.replace(tzinfo=_UTC) if value.tzinfo is None else value.astimezone(_UTC)


def _clamp_offset(tz_offset_minutes: Optional[int]) -> int:
    try:
        minutes = int(tz_offset_minutes or 0)
    except (TypeError, ValueError):
        return 0
    return max(-_MAX_TZ_OFFSET, min(_MAX_TZ_OFFSET, minutes))


def local_today(tz_offset_minutes: Optional[int], now: Optional[datetime] = None) -> date:
    """
    The learner's local date. `tz_offset_minutes` is JavaScript's getTimezoneOffset() (UTC minus
    local, IST = -330), clamped to [-840, 840]; None means UTC. `now` is for tests.
    """
    moment = _aware(now) if now is not None else _utcnow()
    return (moment - timedelta(minutes=_clamp_offset(tz_offset_minutes))).date()


def _is_core(module_id: str) -> bool:
    """Generated (AI / faculty made) modules earn no XP or badges (any spelling of the prefix)."""
    return not str(module_id).casefold().startswith(GENERATED_MODULE_PREFIX)


def _key(module_id: str) -> str:
    """Statistics treat every spelling of an id as the same module / lesson / problem."""
    return str(module_id).casefold()


def _clean_pct(percentage) -> float:
    try:
        pct = float(percentage)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(pct):
        return 0.0
    return max(0.0, min(100.0, pct))


def _meta_dict(meta) -> dict:
    return meta if isinstance(meta, dict) else {}


def _event_exists(db: Session, user_id: int, kind: str, ref_key: str) -> bool:
    return (
        db.query(XPEvent.id)
        .filter(XPEvent.user_id == user_id, XPEvent.kind == kind, XPEvent.ref_key == ref_key)
        .first()
        is not None
    )


def _new_profile(user_id: int) -> GamificationProfile:
    return GamificationProfile(
        user_id=user_id,
        xp_total=0,
        longest_streak=0,
        streak_freezes=0,
        last_active_date=None,
        daily_goal=DEFAULT_DAILY_GOAL,
        daily_xp=0,
        daily_xp_date=None,
        show_on_leaderboard=False,
    )


def _profile_or_default(db: Session, user_id: int) -> GamificationProfile:
    """Read-only access: never creates a row (a transient default profile is returned instead)."""
    return db.get(GamificationProfile, user_id) or _new_profile(user_id)


def _seed_from_legacy_streak(profile: GamificationProfile, user: User, today: date, tz_offset: Optional[int]) -> int:
    """
    Learners that had a (page-view based) streak before gamification existed keep it if it is still
    alive (last bumped within two local days); older ones simply start fresh. Returns the carried
    count (0 when nothing was carried).

    The carried days were not earned by learning, so they are only kept so the streak is not wiped:
    they pay no milestone XP (see _mark_legacy_milestones) and do not seed `longest_streak`, which
    the streak badges read; both follow the streak the learner builds from here.
    """
    count = user.streak_count or 0
    stamp = user.last_streak_update
    if count <= 0 or stamp is None:
        return 0
    legacy_date = (_aware(stamp) - timedelta(minutes=_clamp_offset(tz_offset))).date()
    if 0 <= (today - legacy_date).days <= 2:
        profile.last_active_date = legacy_date
        return count
    return 0


def _profile_for_read(db: Session, user: User, today: date, tz_offset: Optional[int]) -> GamificationProfile:
    """
    Read-only: the stored profile, or (for a learner who has none yet) a transient one that already
    carries a living legacy streak, so reads and the first write agree. Nothing is added to the session.
    """
    profile = db.get(GamificationProfile, user.id)
    if profile is not None:
        return profile
    profile = _new_profile(user.id)
    _seed_from_legacy_streak(profile, user, today, tz_offset)
    return profile


def _mark_legacy_milestones(db: Session, user_id: int, count: int, today: date) -> None:
    """Zero-XP ledger rows that mark every streak milestone the carried streak already passed as paid."""
    for days in STREAK_MILESTONES:
        if days <= count:
            try:
                with db.begin_nested():
                    db.add(XPEvent(
                        user_id=user_id, kind=KIND_STREAK_MILESTONE, ref_key=str(days), amount=0,
                        local_date=today, meta={"days": days, "carried_over": True}, created_at=_utcnow(),
                    ))
            except IntegrityError:
                pass


# --------------------------------------------------------------------------------------
# The learner's local date: sticky offset, never backwards
# --------------------------------------------------------------------------------------


def _resolve_offset(profile: GamificationProfile, requested: Optional[int], now: datetime) -> Tuple[int, bool]:
    """
    (offset to compute local dates with, whether to remember it). The X-TZ-Offset header is chosen by
    the client, so a changed offset is only believed TZ_CHANGE_COOLDOWN after the previous change:
    flipping between UTC-14 and UTC+14 to mint extra days gets nowhere.
    """
    wanted = _clamp_offset(requested)
    stored = profile.tz_offset
    if stored is None:
        return wanted, True
    if wanted == stored:
        return stored, False
    changed = profile.tz_changed_at
    if changed is None or now - _aware(changed) >= TZ_CHANGE_COOLDOWN:
        return wanted, True
    return stored, False


def _no_earlier(profile: GamificationProfile, today: date) -> date:
    """The local date never moves backwards: not behind the learner's last activity or daily-XP day."""
    for known in (profile.last_active_date, profile.daily_xp_date):
        if known is not None and known > today:
            today = known
    return today


def _read_today(profile: Optional[GamificationProfile], tz_offset: Optional[int], now: datetime) -> date:
    """The local date for a read-only request (nothing is remembered)."""
    if profile is None:
        return local_today(tz_offset)
    offset, _ = _resolve_offset(profile, tz_offset, now)
    return _no_earlier(profile, local_today(offset))


def _ensure_profile(db: Session, user: User, today: date, tz_offset: Optional[int]) -> GamificationProfile:
    """Get-or-create the learner's profile; safe when two requests race to create it."""
    profile = db.get(GamificationProfile, user.id)
    if profile is not None:
        return profile
    profile = _new_profile(user.id)
    carried = _seed_from_legacy_streak(profile, user, today, tz_offset)
    try:
        with db.begin_nested():
            db.add(profile)
    except IntegrityError:
        # Another request created it first: use theirs.
        profile = db.get(GamificationProfile, user.id)
        if profile is None:
            raise
        return profile
    if carried:
        _mark_legacy_milestones(db, user.id, carried, today)
    return profile


# --------------------------------------------------------------------------------------
# Per-call context and the atomic award primitive
# --------------------------------------------------------------------------------------


class _Ctx:
    def __init__(self, db: Session, user: User, profile: GamificationProfile, today: date, now: datetime, core: bool):
        self.db = db
        self.user = user
        self.user_id: int = user.id
        self.profile = profile
        self.today = today
        self.now = now
        self.core = core  # this activity may earn XP and badges
        self.events: List[RewardEvent] = []
        self.gained = 0
        self.xp_before: int = profile.xp_total or 0
        self.streak: Optional[StreakResult] = None
        self.milestone: Optional[int] = None
        self.just_met = False
        self.dirty = False  # something badge statistics depend on changed (beyond XP and the streak)
        self.extra_quiz: Dict[str, float] = {}  # quiz % of the current attempt (it may not be persisted yet)


def _award(
    ctx: _Ctx,
    kind: str,
    ref_key: str,
    amount: int,
    meta: Optional[dict] = None,
    *,
    counts_toward_daily: bool = True,
) -> bool:
    """
    Insert one ledger event and bump the cached totals. Returns False when the event was already
    awarded (unique (user_id, kind, ref_key)), in which case nothing changes.
    """
    if len(ref_key) > _MAX_REF_LEN:
        return False
    db = ctx.db
    if _event_exists(db, ctx.user_id, kind, ref_key):
        return False
    event = XPEvent(
        user_id=ctx.user_id,
        kind=kind,
        ref_key=ref_key,
        amount=amount,
        local_date=ctx.today,
        meta=meta or {},
        created_at=ctx.now,
    )
    try:
        with db.begin_nested():  # SAVEPOINT: a lost race rolls back only this insert
            db.add(event)
    except IntegrityError:
        return False
    if amount > 0:
        profile = ctx.profile
        # Atomic SQL expressions (UPDATE ... SET xp_total = xp_total + :amount), never read-modify-write.
        profile.xp_total = GamificationProfile.xp_total + amount
        if counts_toward_daily:
            profile.daily_xp = GamificationProfile.daily_xp + amount
        db.flush()
        ctx.events.append(RewardEvent(kind=kind, label=event_label(kind, ref_key), amount=amount))
        ctx.gained += amount
    return True


# --------------------------------------------------------------------------------------
# Streak / daily bookkeeping shared by every record_* call
# --------------------------------------------------------------------------------------


def _begin(db: Session, user: User, *, today: Optional[date], tz_offset: Optional[int], core: bool) -> _Ctx:
    """
    Lock the learner's profile and work out their local date. An explicit `today` (tests, callers
    that already know it) is used as given; otherwise it comes from the sticky offset. Either way it
    never moves backwards.
    """
    db.flush()  # write anything the caller left pending before we lock and refresh
    account = db.get(User, user.id)
    if account is None:
        raise LookupError(f"user {user.id} not found")
    now = _utcnow()
    _ensure_profile(db, account, today or local_today(tz_offset), tz_offset)
    # Lock the profile row for the rest of the transaction and read it fresh (populate_existing).
    profile = (
        db.query(GamificationProfile)
        .filter(GamificationProfile.user_id == account.id)
        .populate_existing()
        .with_for_update()
        .one()
    )
    db.refresh(account)  # streak_count may have been changed by a request that held the lock before us
    if today is None:
        offset, remember = _resolve_offset(profile, tz_offset, now)
        today = local_today(offset)
        if remember and profile.tz_offset != offset:
            profile.tz_offset = offset
            profile.tz_changed_at = now
    today = _no_earlier(profile, today)
    ctx = _Ctx(db, account, profile, today, now, core)
    if profile.daily_xp_date != today:
        profile.daily_xp = 0
        profile.daily_xp_date = today
    db.flush()
    return ctx


def _apply_streak(ctx: _Ctx) -> None:
    """Count this activity towards the streak and keep users.streak_count / last_streak_update in sync."""
    profile, user = ctx.profile, ctx.user
    last = profile.last_active_date
    result = compute_streak(
        last,
        ctx.today,
        (user.streak_count or 0) if last is not None else 0,
        profile.streak_freezes or 0,
        profile.longest_streak or 0,
    )
    ctx.streak = result
    user.streak_count = result.count
    user.last_streak_update = ctx.now
    profile.streak_freezes = result.freezes
    if result.extended:
        # Only a streak that moved today raises `longest` (the streak badges read it): the days of a
        # carried-over page-view streak are not counted until the learner really extends it.
        profile.longest_streak = result.longest
    if last is None or ctx.today > last:
        profile.last_active_date = ctx.today  # never move backwards on clock skew
    ctx.db.flush()
    if result.comeback:
        # Zero-XP marker feeding the Comeback Kid badge (one per local day).
        _award(ctx, KIND_COMEBACK, ctx.today.isoformat(), 0, {"streak_was": result.broken_from})


def _award_streak_milestone(ctx: _Ctx) -> None:
    result = ctx.streak
    if result is None:
        return
    days = result.milestone
    if days is not None:
        awarded = _award(ctx, KIND_STREAK_MILESTONE, str(days), streak_milestone_xp(days), {"days": days})
    elif result.count in STREAK_MILESTONES and not _event_exists(
        ctx.db, ctx.user_id, KIND_STREAK_MILESTONE, str(result.count)
    ):
        # The day that reached the milestone was spent on a generated module (no XP there): pay it now.
        days = result.count
        awarded = _award(ctx, KIND_STREAK_MILESTONE, str(days), streak_milestone_xp(days), {"days": days})
    else:
        return
    if awarded:
        ctx.milestone = days


def _check_daily_goal(ctx: _Ctx) -> None:
    """Pay the one-off daily-goal bonus the first time the day's XP (excluding the bonus) reaches the goal."""
    profile = ctx.profile
    # No "XP gained just now" condition: the bonus is idempotent through the ledger, and it must also
    # be paid when the goal was lowered below what was already earned today.
    if (profile.daily_xp or 0) < (profile.daily_goal or DEFAULT_DAILY_GOAL):
        return
    if _award(ctx, KIND_DAILY_GOAL, ctx.today.isoformat(), XP_DAILY_GOAL, counts_toward_daily=False):
        ctx.just_met = True


# --------------------------------------------------------------------------------------
# Statistics and badges
# --------------------------------------------------------------------------------------


def _quiz_attempt_rows(db: Session, user_id: int, module_id: Optional[str] = None):
    query = db.query(
        QuizAttempt.id, QuizAttempt.module_id, QuizAttempt.score, QuizAttempt.max_score, QuizAttempt.attempted_at
    ).filter(QuizAttempt.user_id == user_id)
    if module_id is not None:
        query = query.filter(QuizAttempt.module_id == module_id)
    return query.order_by(QuizAttempt.module_id, QuizAttempt.attempted_at, QuizAttempt.id)


def _credited_attempts(rows) -> List[Tuple[int, str, float]]:
    """
    (attempt id, module id, percentage) of the quiz attempts that count towards rewards: per module
    the first one, and every attempt made at least QUIZ_RETRY_COOLDOWN after the previous attempt
    (whether or not that one counted, so hammering the endpoint keeps the learner on cooldown).
    `rows` are ordered by (module_id, attempted_at, id).
    """
    credited: List[Tuple[int, str, float]] = []
    previous: Dict[str, Optional[datetime]] = {}
    for attempt_id, module_id, score, max_score, attempted_at in rows:
        at = _aware(attempted_at) if attempted_at is not None else None
        if module_id in previous:
            before = previous[module_id]
            if before is not None and at is not None and at - before < QUIZ_RETRY_COOLDOWN:
                previous[module_id] = at
                continue
        previous[module_id] = at
        credited.append((attempt_id, module_id, _clean_pct(score / max_score * 100) if max_score else 0.0))
    return credited


def _attempt_credited(db: Session, user_id: int, module_id: str, attempt_id, now: datetime) -> bool:
    """Does this attempt count? (An attempt that is not saved yet counts as made `now`.)"""
    rows = list(_quiz_attempt_rows(db, user_id, module_id))
    if not any(row[0] == attempt_id for row in rows):
        rows.append((attempt_id, module_id, 0.0, 1, now))
    return any(credited_id == attempt_id for credited_id, _, _ in _credited_attempts(rows))


def _best_quiz_pct_by_module(db: Session, user_id: int, extra: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Best quiz percentage per core module (keyed by the lower-cased module id), from the credited
    attempts and from the ledger (plus `extra`, an attempt that is not saved yet).
    """
    best: Dict[str, float] = {}

    def note(module_id: str, pct: float) -> None:
        if _is_core(module_id):
            key = _key(module_id)
            best[key] = max(best.get(key, 0.0), pct)

    for _, module_id, pct in _credited_attempts(_quiz_attempt_rows(db, user_id)):
        note(module_id, pct)
    for ref_key, meta in db.query(XPEvent.ref_key, XPEvent.meta).filter(
        XPEvent.user_id == user_id, XPEvent.kind == KIND_QUIZ
    ):
        pct = _meta_dict(meta).get("percentage")
        if isinstance(pct, (int, float)):
            note(ref_key.partition(":")[0], _clean_pct(pct))
    for module_id, pct in (extra or {}).items():
        note(module_id, pct)
    return best


def _lesson_cutoff(db: Session, user_id: int) -> Optional[datetime]:
    """
    Lesson progress saved up to this moment predates the learner's gamification profile (it was
    recorded before rewards existed for them), so it counts as read. Progress saved afterwards only
    counts when the ledger paid for it: a lesson-view that was throttled does not count as a read.
    """
    created = db.query(GamificationProfile.created_at).filter(GamificationProfile.user_id == user_id).scalar()
    return _aware(created) if created is not None else None


def _legacy_lesson(viewed_at: Optional[datetime], cutoff: Optional[datetime]) -> bool:
    # Every saved lesson view counts as read. The pace rule (LESSON_MIN_GAP) only withholds the XP:
    # the learner sees "Read" everywhere in the product, so badges and module mastery must agree
    # instead of silently never arriving. (The cutoff helper is kept for callers that pass it.)
    return True


def _collect_stats(
    db: Session,
    user_id: int,
    *,
    xp_total: int,
    longest_streak: int,
    extra_quiz: Optional[Dict[str, float]] = None,
) -> dict:
    """The stats snapshot that badge conditions are evaluated against (core modules only)."""
    lessons: Set[Tuple[str, str]] = set()
    cutoff = _lesson_cutoff(db, user_id)
    for module_id, lesson_id, viewed_at in db.query(
        LessonProgress.module_id, LessonProgress.lesson_id, LessonProgress.viewed_at
    ).filter(LessonProgress.user_id == user_id, LessonProgress.is_complete.is_(True)):
        if _is_core(module_id) and _legacy_lesson(viewed_at, cutoff):
            lessons.add((_key(module_id), lesson_id))

    solved: Set[Tuple[str, str]] = set()
    for module_id, problem_id in (
        db.query(CodeSubmission.module_id, CodeSubmission.problem_id)
        .filter(CodeSubmission.user_id == user_id, CodeSubmission.status == SubmissionStatus.PASS)
        .distinct()
    ):
        if _is_core(module_id):
            solved.add((_key(module_id), problem_id))

    perfect = first_try = hard = goals = comebacks = 0
    completed: Set[str] = set()
    for kind, ref_key, meta in db.query(XPEvent.kind, XPEvent.ref_key, XPEvent.meta).filter(
        XPEvent.user_id == user_id, XPEvent.kind.in_(_STAT_KINDS)
    ):
        if kind == KIND_LESSON:
            module_id, _, lesson_id = ref_key.partition("/")
            if _is_core(module_id):
                lessons.add((_key(module_id), lesson_id))
        elif kind == KIND_PROBLEM:
            module_id, _, problem_id = ref_key.partition("/")
            if _is_core(module_id):
                solved.add((_key(module_id), problem_id))
                if _meta_dict(meta).get("difficulty") == "hard":
                    hard += 1
        elif kind == KIND_QUIZ_PERFECT:
            perfect += 1
        elif kind == KIND_FIRST_TRY:
            first_try += 1
        elif kind == KIND_MODULE_COMPLETE:
            completed.add(ref_key)
        elif kind == KIND_DAILY_GOAL:
            goals += 1
        elif kind == KIND_COMEBACK:
            comebacks += 1

    quiz_best = _best_quiz_pct_by_module(db, user_id, extra_quiz)
    return {
        "lessons_read": len(lessons),
        "quizzes_taken": len(quiz_best),
        "quizzes_80": sum(1 for pct in quiz_best.values() if pct >= 80),
        "perfect_quizzes": perfect,
        "problems_solved": len(solved),
        "hard_solved": hard,
        "first_try_solves": first_try,
        "modules_completed": len(completed),
        "completed_modules": completed,
        "daily_goals_met": goals,
        "comebacks": comebacks,
        "longest_streak": longest_streak,
        "level": level_for_xp(xp_total),
        "xp_total": xp_total,
    }


def _badge_info(badge: BadgeDef, stats: Optional[dict], *, earned: bool, earned_at: Optional[datetime]) -> BadgeInfo:
    if earned:
        current = badge.target
    else:
        current = max(0, min(int(badge.current(stats or {})), badge.target))
    return BadgeInfo(
        id=badge.id,
        name=badge.name,
        description=badge.description,
        icon=badge.icon,
        category=badge.category,
        rarity=badge.rarity,
        earned=earned,
        earned_at=_aware(earned_at) if (earned and earned_at is not None) else None,
        progress=BadgeProgress(current=current, target=badge.target),
    )


def _earned_badges(db: Session, user_id: int) -> Dict[str, datetime]:
    return {
        badge_id: earned_at
        for badge_id, earned_at in db.query(UserBadge.badge_id, UserBadge.earned_at).filter(UserBadge.user_id == user_id)
        if badge_id in BADGES_BY_ID
    }


def _evaluate_badges(ctx: _Ctx) -> List[BadgeInfo]:
    """Unlock every badge whose condition now holds; returns the newly earned ones."""
    db, profile = ctx.db, ctx.profile
    stats = _collect_stats(
        db,
        ctx.user_id,
        xp_total=profile.xp_total or 0,
        longest_streak=profile.longest_streak or 0,
        extra_quiz=ctx.extra_quiz,
    )
    already = set(_earned_badges(db, ctx.user_id))
    unlocked: List[BadgeInfo] = []
    for badge in BADGES:
        if badge.id in already or not badge.is_earned(stats):
            continue
        try:
            with db.begin_nested():
                db.add(UserBadge(user_id=ctx.user_id, badge_id=badge.id, earned_at=ctx.now))
        except IntegrityError:
            continue  # unlocked concurrently
        unlocked.append(_badge_info(badge, stats, earned=True, earned_at=ctx.now))
    return unlocked


# --------------------------------------------------------------------------------------
# Module mastery
# --------------------------------------------------------------------------------------


def _module_complete(
    db: Session,
    user_id: int,
    module_id: str,
    detail: ModuleDetail,
    extra_quiz_pct: Optional[float] = None,
) -> bool:
    if not _is_core(module_id):
        return False
    lessons_needed = {d.id for d in detail.docs}
    problems_needed = {p.get("id") for p in detail.problems if isinstance(p, dict)}
    needs_quiz = bool(detail.quiz_id)
    if not (lessons_needed or problems_needed or needs_quiz):
        return False  # an empty module cannot be mastered

    if lessons_needed:
        cutoff = _lesson_cutoff(db, user_id)
        read = {
            lesson_id
            for lesson_id, viewed_at in db.query(LessonProgress.lesson_id, LessonProgress.viewed_at).filter(
                LessonProgress.user_id == user_id,
                LessonProgress.module_id == module_id,
                LessonProgress.is_complete.is_(True),
            )
            if _legacy_lesson(viewed_at, cutoff)
        }
        prefix = f"{module_id}/"
        read |= {
            ref_key[len(prefix):]
            for (ref_key,) in db.query(XPEvent.ref_key).filter(
                XPEvent.user_id == user_id,
                XPEvent.kind == KIND_LESSON,
                XPEvent.ref_key.startswith(prefix, autoescape=True),
            )
        }
        if not lessons_needed <= read:
            return False

    if problems_needed:
        solved = {
            problem_id
            for (problem_id,) in db.query(CodeSubmission.problem_id)
            .filter(
                CodeSubmission.user_id == user_id,
                CodeSubmission.module_id == module_id,
                CodeSubmission.status == SubmissionStatus.PASS,
            )
            .distinct()
        }
        prefix = f"{module_id}/"
        solved |= {
            ref_key[len(prefix):]
            for (ref_key,) in db.query(XPEvent.ref_key).filter(
                XPEvent.user_id == user_id,
                XPEvent.kind == KIND_PROBLEM,
                XPEvent.ref_key.startswith(prefix, autoescape=True),
            )
        }
        if not problems_needed <= solved:
            return False

    if needs_quiz:
        extra = {module_id: extra_quiz_pct} if extra_quiz_pct is not None else None
        if _best_quiz_pct_by_module(db, user_id, extra).get(_key(module_id), 0.0) < MODULE_QUIZ_PASS_PCT:
            return False
    return True


def is_module_complete(db: Session, user_id: int, module_id: str, detail: ModuleDetail) -> bool:
    """
    A module is mastered when every lesson is read, every problem solved and the best quiz score is
    at least 70% (parts a module lacks are ignored). Generated modules never count.
    """
    return _module_complete(db, user_id, module_id, detail)


def _maybe_complete_module(ctx: _Ctx, module_id: str, detail: Optional[ModuleDetail], extra_quiz_pct: Optional[float] = None) -> None:
    if not ctx.core or detail is None:
        return
    if _event_exists(ctx.db, ctx.user_id, KIND_MODULE_COMPLETE, module_id):
        return
    if _module_complete(ctx.db, ctx.user_id, module_id, detail, extra_quiz_pct):
        _award(ctx, KIND_MODULE_COMPLETE, module_id, XP_MODULE_COMPLETE, {"module_id": module_id})


# --------------------------------------------------------------------------------------
# The shared record_* pipeline
# --------------------------------------------------------------------------------------


def _record(db: Session, user: User, module_id: str, *, counts: bool, tz_offset, today, work) -> RewardSummary:
    """
    begin (lock + daily reset) -> streak -> `work(ctx)` (the XP awards) -> streak milestone ->
    daily goal -> badges -> RewardSummary -> commit. Any failure rolls the whole transaction back.
    `counts` False means the activity is not valid (e.g. an unknown lesson): no streak, no XP.
    """
    try:
        ctx = _begin(db, user, today=today, tz_offset=tz_offset, core=counts and _is_core(module_id))
        if counts:
            _apply_streak(ctx)
        work(ctx)
        if ctx.core:
            _award_streak_milestone(ctx)
            _check_daily_goal(ctx)
        # Badge statistics only move when XP was paid, the streak moved or the work flagged a change:
        # a re-read that changed nothing skips the whole statistics snapshot.
        streak = ctx.streak
        changed = ctx.gained > 0 or ctx.dirty or bool(streak and (streak.extended or streak.comeback))
        new_badges = _evaluate_badges(ctx) if ctx.core and changed else []
        summary = _reward_summary(ctx, new_badges)
        db.commit()
        return summary
    except Exception:
        db.rollback()
        raise


def _reward_summary(ctx: _Ctx, new_badges: List[BadgeInfo]) -> RewardSummary:
    db = ctx.db
    db.flush()
    profile, user = ctx.profile, ctx.user
    xp_total = profile.xp_total or 0
    progress = level_progress(xp_total)
    previous_level = level_for_xp(ctx.xp_before)
    result = ctx.streak
    last = profile.last_active_date
    goal = profile.daily_goal or DEFAULT_DAILY_GOAL
    xp_today = profile.daily_xp or 0
    return RewardSummary(
        xp_gained=ctx.gained,
        events=list(ctx.events),
        total_xp=xp_total,
        level=progress.level,
        previous_level=previous_level,
        level_title=progress.title,
        level_up=progress.level > previous_level,
        xp_into_level=progress.xp_into_level,
        xp_for_next_level=progress.xp_for_next_level,
        streak=StreakInfo(
            count=user.streak_count or 0,
            longest=max(profile.longest_streak or 0, user.streak_count or 0),
            freezes=profile.streak_freezes or 0,
            extended=bool(result and result.extended),
            used_freeze=bool(result and result.used_freeze),
            milestone=ctx.milestone,
            broken_from=result.broken_from if result else None,
            active_today=last is not None and last >= ctx.today,
            at_risk=False,
        ),
        new_badges=new_badges,
        daily=DailyInfo(goal=goal, xp_today=xp_today, goal_met=xp_today >= goal, just_met=ctx.just_met),
    )


# --------------------------------------------------------------------------------------
# Public API: recording activity
# --------------------------------------------------------------------------------------


def _lesson_pace_ok(ctx: _Ctx) -> bool:
    """A lesson pays only LESSON_MIN_GAP after the learner's previous paid lesson (no instant bulk 'reads')."""
    last = (
        ctx.db.query(func.max(XPEvent.created_at))
        .filter(XPEvent.user_id == ctx.user_id, XPEvent.kind == KIND_LESSON)
        .scalar()
    )
    return last is None or ctx.now - _aware(last) >= LESSON_MIN_GAP


def record_lesson_read(
    db: Session,
    user: User,
    module_id: str,
    lesson_id: str,
    *,
    detail: Optional[ModuleDetail] = None,
    tz_offset: Optional[int] = None,
    today: Optional[date] = None,
) -> RewardSummary:
    """
    A lesson was read: 10 XP the first time, nothing on re-reads; always streak activity.

    `detail` (the already loaded ModuleDetail) is optional but should be passed: it lets us reject
    lesson ids that do not exist (so XP cannot be farmed with made-up ids) and notice when this
    lesson completed the module. Without it we trust the caller to have validated the ids.
    """
    valid = detail is None or any(d.id == lesson_id for d in detail.docs)

    def work(ctx: _Ctx) -> None:
        if not ctx.core:
            return
        ref = f"{module_id}/{lesson_id}"
        if _event_exists(ctx.db, ctx.user_id, KIND_LESSON, ref) or not _lesson_pace_ok(ctx):
            return  # nothing to pay (a re-read, or faster than anyone can read: it pays when read again)
        if _award(ctx, KIND_LESSON, ref, XP_LESSON, {"module_id": module_id, "lesson_id": lesson_id}):
            ctx.dirty = True
            _maybe_complete_module(ctx, module_id, detail)

    return _record(db, user, module_id, counts=valid, tz_offset=tz_offset, today=today, work=work)


def record_quiz_attempt(
    db: Session,
    user: User,
    module_id: str,
    attempt_id,
    percentage: float,
    *,
    detail: ModuleDetail,
    tz_offset: Optional[int] = None,
    today: Optional[date] = None,
) -> RewardSummary:
    """
    A quiz was submitted (the QuizAttempt row should already be saved). Quiz XP is a delta: the
    module is worth round(50 * best% / 100) in total, an attempt only earns what has not been paid
    yet, and a 100% score earns the one-off perfect bonus.
    """
    pct = _clean_pct(percentage)

    def work(ctx: _Ctx) -> None:
        if not ctx.core:
            return
        if not _attempt_credited(ctx.db, ctx.user_id, module_id, attempt_id, ctx.now):
            return  # too soon after the previous attempt: graded and saved, but it pays nothing
        ctx.dirty = True
        ctx.extra_quiz[module_id] = pct
        best = _best_quiz_pct_by_module(ctx.db, ctx.user_id, ctx.extra_quiz).get(_key(module_id), pct)
        paid = (
            ctx.db.query(func.coalesce(func.sum(XPEvent.amount), 0))
            .filter(
                XPEvent.user_id == ctx.user_id,
                XPEvent.kind == KIND_QUIZ,
                XPEvent.ref_key.startswith(f"{module_id}:", autoescape=True),
            )
            .scalar()
        )
        delta = quiz_target_xp(best) - int(paid or 0)
        if delta > 0:
            _award(
                ctx, KIND_QUIZ, f"{module_id}:{attempt_id}", delta,
                {"module_id": module_id, "percentage": round(pct, 2), "best": round(best, 2)},
            )
        if pct >= 99.999:
            _award(ctx, KIND_QUIZ_PERFECT, module_id, XP_QUIZ_PERFECT, {"module_id": module_id})
        _maybe_complete_module(ctx, module_id, detail, extra_quiz_pct=pct)

    return _record(db, user, module_id, counts=bool(detail.quiz_id), tz_offset=tz_offset, today=today, work=work)


def record_problem_submission(
    db: Session,
    user: User,
    module_id: str,
    problem_id: str,
    *,
    difficulty: str,
    passed: bool,
    prior_submissions: int,
    detail: ModuleDetail,
    tz_offset: Optional[int] = None,
    today: Optional[date] = None,
) -> RewardSummary:
    """
    Code was graded (pass or fail: both are streak activity). The first PASS earns XP by difficulty
    and, if it was the learner's very first submission for the problem (`prior_submissions` is the
    number of submissions BEFORE this one), the first-try bonus.
    """
    known = any(isinstance(p, dict) and p.get("id") == problem_id for p in detail.problems)

    def work(ctx: _Ctx) -> None:
        if not (ctx.core and passed):
            return
        level = normalise_difficulty(difficulty)
        ref = f"{module_id}/{problem_id}"
        meta = {"module_id": module_id, "problem_id": problem_id, "difficulty": level}
        if _award(ctx, KIND_PROBLEM, ref, problem_xp(level), meta):
            if prior_submissions == 0:
                _award(ctx, KIND_FIRST_TRY, ref, XP_FIRST_TRY, meta)
        _maybe_complete_module(ctx, module_id, detail)

    return _record(db, user, module_id, counts=known, tz_offset=tz_offset, today=today, work=work)


# --------------------------------------------------------------------------------------
# Public API: reading
# --------------------------------------------------------------------------------------


def _effective_streak(profile: GamificationProfile, raw_count: int, today: date) -> Tuple[int, bool, bool]:
    """(count to display, active_today, at_risk): a streak that has already lapsed shows as 0."""
    last = profile.last_active_date
    if last is None:
        return 0, False, False
    gap = (today - last).days
    if gap <= 0:
        return max(raw_count, 1), True, False
    if gap == 1:
        return raw_count, False, raw_count >= 1
    if gap == 2 and (profile.streak_freezes or 0) > 0:
        return raw_count, False, False  # a freeze will bridge yesterday
    return 0, False, False


def _weekly_series(db: Session, user_id: int, today: date) -> List[WeeklyPoint]:
    start = today - timedelta(days=6)
    totals = {
        local: int(total or 0)
        for local, total in db.query(XPEvent.local_date, func.sum(XPEvent.amount))
        .filter(XPEvent.user_id == user_id, XPEvent.local_date >= start, XPEvent.local_date <= today)
        .group_by(XPEvent.local_date)
    }
    points = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        points.append(WeeklyPoint(date=day.isoformat(), xp=totals.get(day, 0)))
    return points


def get_summary(
    db: Session,
    user: User,
    *,
    tz_offset: Optional[int] = None,
    today: Optional[date] = None,
) -> GamificationSummary:
    stored = db.get(GamificationProfile, user.id)
    if today is None:
        today = _read_today(stored, tz_offset, _utcnow())
    # A learner without a profile yet still sees the streak they carry over (reads and writes agree).
    profile = stored or _profile_for_read(db, user, today, tz_offset)
    today = _no_earlier(profile, today)
    xp_total = profile.xp_total or 0
    progress = level_progress(xp_total)

    raw = (user.streak_count or 0) if profile.last_active_date is not None else 0
    count, active_today, at_risk = _effective_streak(profile, raw, today)
    goal = profile.daily_goal or DEFAULT_DAILY_GOAL
    xp_today = (profile.daily_xp or 0) if profile.daily_xp_date == today else 0

    earned_rows = [
        (badge_id, earned_at)
        for badge_id, earned_at in db.query(UserBadge.badge_id, UserBadge.earned_at)
        .filter(UserBadge.user_id == user.id)
        .order_by(UserBadge.earned_at.desc(), UserBadge.id.desc())
        if badge_id in BADGES_BY_ID
    ]
    recent_badges = [
        _badge_info(BADGES_BY_ID[badge_id], None, earned=True, earned_at=earned_at)
        for badge_id, earned_at in earned_rows[:RECENT_BADGES]
    ]

    events = (
        db.query(XPEvent)
        .filter(XPEvent.user_id == user.id, XPEvent.amount > 0)
        .order_by(XPEvent.created_at.desc(), XPEvent.id.desc())
        .limit(RECENT_EVENTS)
        .all()
    )
    recent_events = [
        RecentEvent(kind=e.kind, label=event_label(e.kind, e.ref_key), amount=e.amount, created_at=_aware(e.created_at))
        for e in events
    ]

    return GamificationSummary(
        xp_total=xp_total,
        level=progress.level,
        level_title=progress.title,
        xp_into_level=progress.xp_into_level,
        xp_for_next_level=progress.xp_for_next_level,
        next_level_xp=progress.next_level_xp,
        streak=StreakInfo(
            count=count,
            longest=max(profile.longest_streak or 0, count),
            freezes=profile.streak_freezes or 0,
            active_today=active_today,
            at_risk=at_risk,
        ),
        daily=DailyInfo(goal=goal, xp_today=xp_today, goal_met=xp_today >= goal),
        weekly=_weekly_series(db, user.id, today),
        badges_earned=len(earned_rows),
        badges_total=len(BADGES),
        recent_badges=recent_badges,
        recent_events=recent_events,
        show_on_leaderboard=bool(profile.show_on_leaderboard),
    )


def list_badges(db: Session, user: User) -> List[BadgeInfo]:
    """The whole catalogue (catalogue order) with earned flags and progress."""
    profile = _profile_or_default(db, user.id)
    stats = _collect_stats(
        db, user.id, xp_total=profile.xp_total or 0, longest_streak=profile.longest_streak or 0
    )
    earned = _earned_badges(db, user.id)
    return [
        _badge_info(badge, stats, earned=badge.id in earned, earned_at=earned.get(badge.id))
        for badge in BADGES
    ]


def get_leaderboard(
    db: Session,
    user: User,
    *,
    tz_offset: Optional[int] = None,
    now: Optional[datetime] = None,
) -> LeaderboardResponse:
    """
    Weekly (rolling 7 days) XP among opted-in learners: anonymised names, ties share the better
    rank and are ordered by name, top 10 plus the caller's own rank in `me`.

    The aggregation runs in SQL (served by ix_xp_events_created): only the learners at or above the
    10th-highest weekly total are loaded into Python, however many have opted in.
    """
    since = (_aware(now) if now is not None else _utcnow()) - timedelta(days=LEADERBOARD_DAYS)
    weekly = (
        select(XPEvent.user_id.label("user_id"), func.sum(XPEvent.amount).label("total"))
        .join(GamificationProfile, GamificationProfile.user_id == XPEvent.user_id)
        .where(
            GamificationProfile.show_on_leaderboard.is_(True),
            XPEvent.created_at >= since,
            XPEvent.amount > 0,
        )
        .group_by(XPEvent.user_id)
        .subquery()
    )

    top = db.execute(
        select(weekly.c.total).order_by(weekly.c.total.desc(), weekly.c.user_id).limit(LEADERBOARD_SIZE)
    ).all()
    # Everyone tied with the 10th place may still make the top 10 (ties are ordered by name below).
    threshold = int(top[-1][0]) if len(top) >= LEADERBOARD_SIZE else 1
    rows = db.execute(
        select(weekly.c.user_id, weekly.c.total, User.full_name, GamificationProfile.xp_total)
        .join(User, User.id == weekly.c.user_id)
        .join(GamificationProfile, GamificationProfile.user_id == weekly.c.user_id)
        .where(weekly.c.total >= threshold)
    ).all()
    people = sorted(
        (
            (int(total or 0), anonymise_name(full_name), uid, level_for_xp(xp_total or 0))
            for uid, total, full_name, xp_total in rows
        ),
        key=lambda p: (-p[0], p[1].casefold(), p[2]),
    )

    ranked: List[Tuple[int, int, str, int, int]] = []  # rank, xp, name, user_id, level
    previous_xp: Optional[int] = None
    previous_rank = 0
    for position, (xp, name, uid, level) in enumerate(people, start=1):
        rank = previous_rank if xp == previous_xp else position
        ranked.append((rank, xp, name, uid, level))
        previous_xp, previous_rank = xp, rank

    profile = _profile_or_default(db, user.id)
    opted_in = bool(profile.show_on_leaderboard)
    my_xp = int(
        db.query(func.coalesce(func.sum(XPEvent.amount), 0))
        .filter(XPEvent.user_id == user.id, XPEvent.created_at >= since, XPEvent.amount > 0)
        .scalar()
        or 0
    )
    my_rank: Optional[int] = None
    if opted_in:
        # Ties share the better rank; opted in with no XP yet shares last place (after everyone ranked).
        ahead = db.execute(select(func.count()).select_from(weekly).where(weekly.c.total > my_xp)).scalar() or 0
        my_rank = int(ahead) + 1

    entries = [
        LeaderboardEntry(rank=rank, name=name, xp=xp, level=level, is_me=uid == user.id)
        for rank, xp, name, uid, level in ranked[:LEADERBOARD_SIZE]
    ]
    return LeaderboardResponse(
        period="week",
        entries=entries,
        me=LeaderboardMe(rank=my_rank, xp=my_xp, opted_in=opted_in),
    )


def update_settings(
    db: Session,
    user: User,
    update: Union[SettingsUpdate, dict],
    *,
    tz_offset: Optional[int] = None,
    today: Optional[date] = None,
) -> GamificationSummary:
    """Change the daily goal and/or the leaderboard opt-in. Raises ValueError on invalid input."""
    raw = update.model_dump(exclude_unset=True) if isinstance(update, BaseModel) else dict(update)
    clean = SettingsUpdate.model_validate(raw)  # re-validate: model_construct() bypasses the validators
    try:
        ctx = _begin(db, user, today=today, tz_offset=tz_offset, core=True)  # locks the profile; not streak activity
        profile = ctx.profile
        if clean.daily_goal is not None:
            profile.daily_goal = clean.daily_goal
        if clean.show_on_leaderboard is not None:
            profile.show_on_leaderboard = clean.show_on_leaderboard
        # A lowered goal may already be met by today's XP: pay the (one-off, idempotent) bonus now
        # instead of showing "goal complete" without it.
        _check_daily_goal(ctx)
        if ctx.gained > 0:
            _evaluate_badges(ctx)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return get_summary(db, user, tz_offset=tz_offset, today=today)
