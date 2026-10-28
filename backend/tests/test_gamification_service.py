"""
Gamification service tests on an in-memory SQLite database (see conftest.py), plus the HTTP layer.

The tests drive the service the way the endpoints do: save the learner's progress row first, then
call record_*, passing an explicit local date (`today=`) so time is fully under control.
"""
import itertools
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import event, func

from app.core.deps import get_current_user, get_db, get_tz_offset
from app.main import app
from app.models.gamification import GamificationProfile, UserBadge, XPEvent
from app.models.progress import CodeSubmission, LessonProgress, QuizAttempt, SubmissionStatus
from app.schemas.gamification import SettingsUpdate
from app.schemas.module import DocMeta, ModuleDetail
from app.services import gamification as g
from tests.conftest import make_user

MODULE = "module-1-introduction-to-python"
BASE = date(2026, 3, 2)  # a Monday; every test starts its own clock here


def day(n: int) -> date:
    return BASE + timedelta(days=n)


def make_detail(module_id=MODULE, lessons=("l1", "l2"), problems=("p1", "p2", "p3"), quiz=True) -> ModuleDetail:
    return ModuleDetail(
        id=module_id,
        title="Test module",
        description="",
        order=1,
        icon="terminal",
        docs=[DocMeta(id=lid, title=lid.upper(), order=i) for i, lid in enumerate(lessons, start=1)],
        quiz_id=f"{module_id}-quiz" if quiz else None,
        problems=[{"id": pid, "title": pid.upper(), "concepts": []} for pid in problems],
        is_generative=module_id.startswith("generated-"),
    )


DETAIL = make_detail()
GENERATED = "generated-my-notes"
GEN_DETAIL = make_detail(GENERATED, lessons=("g1", "g2"), problems=("gp1",))


# ---- helpers that mirror what the endpoints do --------------------------------------------


def read_lesson(db, user, lesson_id="l1", *, on=BASE, module=MODULE, detail=DETAIL):
    exists = (
        db.query(LessonProgress)
        .filter_by(user_id=user.id, module_id=module, lesson_id=lesson_id)
        .first()
    )
    if not exists:
        db.add(LessonProgress(user_id=user.id, module_id=module, lesson_id=lesson_id))
        db.commit()
    return g.record_lesson_read(db, user, module, lesson_id, detail=detail, today=on)


def take_quiz(db, user, pct, *, on=BASE, module=MODULE, detail=DETAIL, at=None):
    attempt = QuizAttempt(
        user_id=user.id, module_id=module, quiz_id=f"{module}-quiz",
        answers={}, score=pct, max_score=100, per_question_results=[],
    )
    if at is not None:
        attempt.attempted_at = at  # when the attempt was made (the retry cooldown looks at this)
    db.add(attempt)
    db.commit()
    return g.record_quiz_attempt(db, user, module, attempt.id, pct, detail=detail, today=on)


def submit_code(db, user, problem_id, *, passed=True, difficulty="easy", on=BASE, module=MODULE, detail=DETAIL):
    prior = db.query(CodeSubmission).filter_by(user_id=user.id, module_id=module, problem_id=problem_id).count()
    db.add(CodeSubmission(
        user_id=user.id, module_id=module, problem_id=problem_id, code="print(1)",
        status=SubmissionStatus.PASS if passed else SubmissionStatus.FAIL,
    ))
    db.commit()
    return g.record_problem_submission(
        db, user, module, problem_id,
        difficulty=difficulty, passed=passed, prior_submissions=prior, detail=detail, today=on,
    )


def kinds(summary):
    """{kind: amount} of the events in a RewardSummary."""
    return {e.kind: e.amount for e in summary.events}


def ledger(db, user):
    return db.query(XPEvent).filter_by(user_id=user.id).all()


def assert_ledger_consistent(db, user):
    """The cached xp_total must always equal the sum of the ledger."""
    db.expire_all()
    total = db.query(func.coalesce(func.sum(XPEvent.amount), 0)).filter_by(user_id=user.id).scalar()
    profile = db.get(GamificationProfile, user.id)
    assert profile.xp_total == total


@pytest.fixture(autouse=True)
def _plain_xp_rules(no_farming_delays):
    """Most tests are about the XP rules, not the time guards (those have their own tests)."""


@pytest.fixture
def user(db):
    return make_user(db)


# --------------------------------------------------------------------------------------
# Local date
# --------------------------------------------------------------------------------------


def test_local_today_applies_the_browser_offset():
    now = datetime(2026, 3, 1, 20, 0, tzinfo=timezone.utc)
    assert g.local_today(-330, now) == date(2026, 3, 2)  # IST is UTC+5:30, already past midnight
    assert g.local_today(0, now) == date(2026, 3, 1)
    assert g.local_today(300, now) == date(2026, 3, 1)  # US Eastern (UTC-5)
    assert g.local_today(None, now) == date(2026, 3, 1)


def test_local_today_clamps_the_offset_and_accepts_naive_utc():
    now = datetime(2026, 3, 1, 10, 0)  # naive means UTC
    assert g.local_today(5000, now) == g.local_today(840, now) == date(2026, 2, 28)
    assert g.local_today(-5000, now) == g.local_today(-840, now) == date(2026, 3, 2)


def test_local_today_defaults_to_the_current_utc_date():
    before = datetime.now(timezone.utc).date()
    result = g.local_today(0)
    after = datetime.now(timezone.utc).date()
    assert before <= result <= after


# --------------------------------------------------------------------------------------
# Lessons, idempotency and the ledger
# --------------------------------------------------------------------------------------


def test_reading_a_lesson_earns_ten_xp_once(db, user):
    first = read_lesson(db, user, "l1")
    assert first.xp_gained == 10
    assert kinds(first) == {"lesson": 10}
    assert first.events[0].label == "Lesson read"
    assert first.total_xp == 10
    assert (first.level, first.previous_level, first.level_up) == (1, 1, False)

    second = read_lesson(db, user, "l1")
    assert second.xp_gained == 0 and second.events == []
    assert second.total_xp == 10

    assert db.query(XPEvent).filter_by(user_id=user.id, kind="lesson").count() == 1
    assert_ledger_consistent(db, user)


def test_a_different_lesson_earns_again(db, user):
    read_lesson(db, user, "l1")
    assert read_lesson(db, user, "l2").xp_gained == 10


def test_record_without_detail_trusts_the_caller(db, user):
    r = g.record_lesson_read(db, user, MODULE, "anything", today=BASE)
    assert r.xp_gained == 10


def test_unknown_lessons_earn_nothing_and_do_not_count_as_activity(db, user):
    r = g.record_lesson_read(db, user, MODULE, "made-up-lesson", detail=DETAIL, today=BASE)
    assert r.xp_gained == 0 and r.events == []
    assert r.streak.count == 0 and not r.streak.extended and not r.streak.active_today
    assert ledger(db, user) == []
    assert db.get(GamificationProfile, user.id).last_active_date is None


def test_overlong_ids_cannot_overflow_the_ledger(db, user):
    r = g.record_lesson_read(db, user, MODULE, "x" * 400, today=BASE)
    assert r.xp_gained == 0
    assert ledger(db, user) == []


def test_xp_total_is_updated_with_an_sql_expression(db, user):
    statements = []

    @event.listens_for(db.get_bind(), "before_cursor_execute")
    def capture(conn, cursor, statement, parameters, context, executemany):
        statements.append(" ".join(statement.split()))

    read_lesson(db, user, "l1")
    updates = [s for s in statements if s.startswith("UPDATE gamification_profiles SET xp_total=")]
    assert updates and "gamification_profiles.xp_total + ?" in updates[0]


def test_a_lost_award_race_is_swallowed_by_the_unique_constraint(db, user, monkeypatch):
    read_lesson(db, user, "l1")
    # Pretend the existence pre-check was stale: the INSERT itself must then be rejected and rolled
    # back (only its savepoint), leaving the session and the totals untouched.
    monkeypatch.setattr(g, "_event_exists", lambda *a, **k: False)
    r = g.record_lesson_read(db, user, MODULE, "l1", detail=DETAIL, today=BASE)
    assert r.xp_gained == 0 and r.events == []
    assert r.total_xp == 10
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="lesson").count() == 1
    assert_ledger_consistent(db, user)


def test_profile_creation_survives_a_concurrent_create(db, user, monkeypatch):
    real_get = db.get
    seen = {"hidden": False}

    def get_that_misses_once(entity, ident, *args, **kwargs):
        if entity is GamificationProfile and not seen["hidden"]:
            seen["hidden"] = True
            # Another request creates the row right before we try to.
            db.execute(GamificationProfile.__table__.insert().values(user_id=user.id, xp_total=0))
            return None
        return real_get(entity, ident, *args, **kwargs)

    monkeypatch.setattr(db, "get", get_that_misses_once)
    r = g.record_lesson_read(db, user, MODULE, "l1", today=BASE)
    assert r.xp_gained == 10
    assert db.query(GamificationProfile).filter_by(user_id=user.id).count() == 1


def test_a_failure_rolls_everything_back(db, user, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("badge evaluation exploded")

    monkeypatch.setattr(g, "_evaluate_badges", boom)
    with pytest.raises(RuntimeError):
        read_lesson(db, user, "l1")
    monkeypatch.undo()
    assert db.query(XPEvent).filter_by(user_id=user.id).count() == 0
    # ...and the learner can simply try again.
    assert read_lesson(db, user, "l1").xp_gained == 10


# --------------------------------------------------------------------------------------
# Quizzes
# --------------------------------------------------------------------------------------


def test_quiz_xp_is_a_delta_against_what_was_already_paid(db, user):
    first = take_quiz(db, user, 40)
    assert kinds(first)["quiz"] == 20 and "quiz_perfect" not in kinds(first)

    better = take_quiz(db, user, 100)
    assert kinds(better)["quiz"] == 30  # 50 - 20
    assert kinds(better)["quiz_perfect"] == 25

    again = take_quiz(db, user, 100)
    assert "quiz" not in kinds(again) and "quiz_perfect" not in kinds(again)

    worse = take_quiz(db, user, 60)
    assert "quiz" not in kinds(worse)

    events = {e.kind: 0 for e in ledger(db, user)}
    for e in ledger(db, user):
        events[e.kind] += e.amount
    assert events["quiz"] == 50 and events["quiz_perfect"] == 25
    assert_ledger_consistent(db, user)


def test_a_lower_score_after_a_better_one_earns_nothing(db, user):
    take_quiz(db, user, 80)
    r = take_quiz(db, user, 40)
    assert r.xp_gained == 0


def test_replaying_the_same_quiz_attempt_awards_once(db, user):
    attempt = QuizAttempt(user_id=user.id, module_id=MODULE, quiz_id="q", answers={}, score=60, max_score=100, per_question_results=[])
    db.add(attempt)
    db.commit()
    first = g.record_quiz_attempt(db, user, MODULE, attempt.id, 60, detail=DETAIL, today=BASE)
    again = g.record_quiz_attempt(db, user, MODULE, attempt.id, 60, detail=DETAIL, today=BASE)
    assert kinds(first)["quiz"] == 30
    assert again.xp_gained == 0


def test_quiz_xp_works_when_the_attempt_row_is_not_saved_yet(db, user):
    first = g.record_quiz_attempt(db, user, MODULE, 1, 40, detail=DETAIL, today=BASE)
    second = g.record_quiz_attempt(db, user, MODULE, 2, 100, detail=DETAIL, today=BASE)
    third = g.record_quiz_attempt(db, user, MODULE, 3, 100, detail=DETAIL, today=BASE)
    assert kinds(first)["quiz"] == 20
    assert kinds(second)["quiz"] == 30 and kinds(second)["quiz_perfect"] == 25
    assert "quiz" not in kinds(third)


def test_quiz_totals_are_tracked_per_module(db, user):
    other_detail = make_detail("module-2-operators-decision-making")
    take_quiz(db, user, 100)
    r = take_quiz(db, user, 100, module="module-2-operators-decision-making", detail=other_detail)
    assert kinds(r)["quiz"] == 50 and kinds(r)["quiz_perfect"] == 25


def test_quiz_ledger_matching_does_not_treat_underscores_as_wildcards(db, user):
    a, b = make_detail("mod_a"), make_detail("modXa")
    take_quiz(db, user, 100, module="mod_a", detail=a)
    r = take_quiz(db, user, 100, module="modXa", detail=b)
    assert kinds(r)["quiz"] == 50  # not reduced by the XP paid for mod_a


def test_quiz_rejects_nonsense_percentages(db, user):
    assert g.record_quiz_attempt(db, user, MODULE, 1, float("nan"), detail=DETAIL, today=BASE).xp_gained == 0
    r = g.record_quiz_attempt(db, user, MODULE, 2, 400, detail=DETAIL, today=BASE)
    assert kinds(r)["quiz"] == 50  # clamped to 100%


# --------------------------------------------------------------------------------------
# Problems
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "difficulty, xp",
    [("easy", 20), ("medium", 35), ("hard", 60), ("HARD", 60), ("mystery", 20)],
)
def test_problem_xp_by_difficulty_with_first_try_bonus(db, user, difficulty, xp):
    r = submit_code(db, user, "p1", difficulty=difficulty)
    assert kinds(r)["problem"] == xp
    assert kinds(r)["problem_first_try"] == 10


def test_fail_then_pass_has_no_first_try_bonus(db, user):
    failed = submit_code(db, user, "p1", passed=False)
    assert failed.xp_gained == 0 and failed.events == []
    assert failed.streak.count == 1 and failed.streak.extended  # a graded failure still counts as activity

    passed = submit_code(db, user, "p1", passed=True)
    assert kinds(passed)["problem"] == 20
    assert "problem_first_try" not in kinds(passed)
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="problem_first_try").count() == 0


def test_solving_again_earns_nothing(db, user):
    submit_code(db, user, "p1")
    again = submit_code(db, user, "p1")
    assert "problem" not in kinds(again) and "problem_first_try" not in kinds(again)
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="problem").count() == 1


def test_replaying_a_first_try_request_awards_once(db, user):
    first = g.record_problem_submission(
        db, user, MODULE, "p1", difficulty="easy", passed=True, prior_submissions=0, detail=DETAIL, today=BASE
    )
    replay = g.record_problem_submission(
        db, user, MODULE, "p1", difficulty="easy", passed=True, prior_submissions=0, detail=DETAIL, today=BASE
    )
    assert kinds(first)["problem"] == 20 and kinds(first)["problem_first_try"] == 10
    assert replay.xp_gained == 0
    assert_ledger_consistent(db, user)


def test_unknown_problems_earn_nothing(db, user):
    r = g.record_problem_submission(
        db, user, MODULE, "not-a-problem", difficulty="hard", passed=True, prior_submissions=0, detail=DETAIL, today=BASE
    )
    assert r.xp_gained == 0 and ledger(db, user) == []


def test_ledger_remembers_the_difficulty_for_the_hard_badges(db, user):
    submit_code(db, user, "p1", difficulty="hard")
    event_row = db.query(XPEvent).filter_by(user_id=user.id, kind="problem").one()
    assert event_row.meta["difficulty"] == "hard"
    assert event_row.ref_key == f"{MODULE}/p1"
    badges = {b.id: b for b in g.list_badges(db, user)}
    assert badges["hard-solve"].earned and not badges["hard-5"].earned
    assert badges["hard-5"].progress.current == 1


# --------------------------------------------------------------------------------------
# Streaks
# --------------------------------------------------------------------------------------


def test_every_kind_of_activity_extends_the_streak(db, user):
    assert read_lesson(db, user, "l1", on=day(0)).streak.count == 1
    assert take_quiz(db, user, 50, on=day(1)).streak.count == 2
    assert submit_code(db, user, "p1", passed=False, on=day(2)).streak.count == 3


def test_streak_state_is_mirrored_on_the_user(db, user):
    read_lesson(db, user, "l1", on=day(0))
    read_lesson(db, user, "l2", on=day(1))
    db.refresh(user)
    assert user.streak_count == 2
    assert user.last_streak_update is not None
    profile = db.get(GamificationProfile, user.id)
    assert profile.last_active_date == day(1) and profile.longest_streak == 2


def test_streak_over_several_days_with_a_freeze_and_a_break(db, user):
    results = [g.record_lesson_read(db, user, MODULE, f"lesson-{i}", today=day(i)) for i in range(7)]
    assert [r.streak.count for r in results] == [1, 2, 3, 4, 5, 6, 7]
    assert results[2].streak.milestone == 3 and kinds(results[2])["streak_milestone"] == 15
    assert results[6].streak.milestone == 7 and kinds(results[6])["streak_milestone"] == 50
    assert results[6].streak.freezes == 1  # earned at seven days
    assert results[1].streak.milestone is None

    # day 7 is skipped; the freeze bridges it
    bridged = g.record_lesson_read(db, user, MODULE, "lesson-8", today=day(8))
    assert bridged.streak.used_freeze and bridged.streak.extended
    assert (bridged.streak.count, bridged.streak.freezes, bridged.streak.longest) == (8, 0, 8)
    assert bridged.streak.broken_from is None

    # a missed day with no freeze left breaks it
    nine = g.record_lesson_read(db, user, MODULE, "lesson-9", today=day(9))
    assert nine.streak.count == 9
    broken = g.record_lesson_read(db, user, MODULE, "lesson-11", today=day(11))
    assert broken.streak.broken_from == 9
    assert (broken.streak.count, broken.streak.longest, broken.streak.freezes) == (1, 9, 0)
    db.refresh(user)
    assert user.streak_count == 1


def test_streak_milestones_pay_once_ever(db, user):
    for i in range(3):
        g.record_lesson_read(db, user, MODULE, f"a{i}", today=day(i))
    # lose the streak, then build it up to three days again
    g.record_lesson_read(db, user, MODULE, "b0", today=day(10))
    g.record_lesson_read(db, user, MODULE, "b1", today=day(11))
    again = g.record_lesson_read(db, user, MODULE, "b2", today=day(12))
    assert again.streak.count == 3
    assert again.streak.milestone is None and "streak_milestone" not in kinds(again)
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="streak_milestone").count() == 1


def test_same_day_activity_does_not_change_the_streak(db, user):
    read_lesson(db, user, "l1", on=day(0))
    read_lesson(db, user, "l1", on=day(1))
    second = read_lesson(db, user, "l2", on=day(1))
    assert second.streak.count == 2 and not second.streak.extended


def test_clock_skew_never_breaks_a_streak(db, user):
    for i in range(3):
        g.record_lesson_read(db, user, MODULE, f"s{i}", today=day(i))
    behind = g.record_lesson_read(db, user, MODULE, "s9", today=day(1))  # the device clock went back a day
    assert behind.streak.count == 3 and not behind.streak.extended and behind.streak.broken_from is None
    assert db.get(GamificationProfile, user.id).last_active_date == day(2)
    ahead = g.record_lesson_read(db, user, MODULE, "s10", today=day(3))
    assert ahead.streak.count == 4


def test_a_week_away_records_a_comeback(db, user):
    for i in range(3):
        g.record_lesson_read(db, user, MODULE, f"a{i}", today=day(i))
    back = g.record_lesson_read(db, user, MODULE, "back", today=day(2 + 7))
    assert back.streak.count == 1 and back.streak.broken_from == 3
    marker = db.query(XPEvent).filter_by(user_id=user.id, kind="comeback").one()
    assert marker.amount == 0 and marker.ref_key == day(9).isoformat()
    assert "comeback" in [b.id for b in back.new_badges]
    assert all(e.kind != "comeback" for e in back.events)  # a marker, never a toast

    # the same day again does not add a second marker
    g.record_lesson_read(db, user, MODULE, "back2", today=day(9))
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="comeback").count() == 1


def test_six_days_away_is_not_a_comeback(db, user):
    g.record_lesson_read(db, user, MODULE, "a", today=day(0))
    g.record_lesson_read(db, user, MODULE, "b", today=day(6))
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="comeback").count() == 0


def test_a_living_legacy_streak_is_carried_over(db, user):
    user.streak_count = 4
    user.last_streak_update = datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)
    db.commit()
    r = g.record_lesson_read(db, user, MODULE, "l1", today=day(0))
    assert r.streak.count == 5 and r.streak.longest == 5


def test_a_stale_legacy_streak_starts_fresh(db, user):
    user.streak_count = 12
    user.last_streak_update = datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc)
    db.commit()
    r = g.record_lesson_read(db, user, MODULE, "l1", today=day(0))
    assert r.streak.count == 1 and r.streak.broken_from is None


# --------------------------------------------------------------------------------------
# Daily goal
# --------------------------------------------------------------------------------------


def test_daily_goal_bonus_fires_once_per_local_day_and_is_excluded_from_daily_xp(db, user):
    g.update_settings(db, user, SettingsUpdate(daily_goal=20), today=day(0))

    first = g.record_lesson_read(db, user, MODULE, "a1", today=day(0))
    assert (first.daily.goal, first.daily.xp_today) == (20, 10)
    assert not first.daily.goal_met and not first.daily.just_met

    second = g.record_lesson_read(db, user, MODULE, "a2", today=day(0))
    assert kinds(second) == {"lesson": 10, "daily_goal": 10}
    assert second.xp_gained == 20 and second.total_xp == 30
    assert second.daily.just_met and second.daily.goal_met
    assert second.daily.xp_today == 20  # the bonus itself does not count towards the day's XP

    third = g.record_lesson_read(db, user, MODULE, "a3", today=day(0))
    assert kinds(third) == {"lesson": 10}
    assert third.daily.goal_met and not third.daily.just_met and third.daily.xp_today == 30
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="daily_goal").count() == 1

    # next local day: the counter resets and the bonus can fire again
    next_day = g.record_lesson_read(db, user, MODULE, "b1", today=day(1))
    assert next_day.daily.xp_today == 10 and not next_day.daily.goal_met
    again = g.record_lesson_read(db, user, MODULE, "b2", today=day(1))
    assert again.daily.just_met and kinds(again)["daily_goal"] == 10
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="daily_goal").count() == 2
    assert_ledger_consistent(db, user)


def test_default_daily_goal_is_thirty(db, user):
    r = read_lesson(db, user, "l1")
    assert r.daily.goal == 30


def test_one_big_award_can_cross_the_goal(db, user):
    r = submit_code(db, user, "p1", difficulty="hard")  # 60 + 10 first try
    assert r.daily.just_met and kinds(r)["daily_goal"] == 10
    assert r.daily.xp_today == 70


def test_streak_bonus_counts_towards_the_daily_goal(db, user):
    g.update_settings(db, user, SettingsUpdate(daily_goal=20), today=day(0))
    g.record_lesson_read(db, user, MODULE, "a", today=day(0))
    g.record_lesson_read(db, user, MODULE, "b", today=day(1))
    r = g.record_lesson_read(db, user, MODULE, "c", today=day(2))  # 10 + 15 streak milestone
    assert kinds(r) == {"lesson": 10, "streak_milestone": 15, "daily_goal": 10}
    assert r.daily.xp_today == 25


# --------------------------------------------------------------------------------------
# Levels
# --------------------------------------------------------------------------------------


def test_level_up_is_reported(db, user):
    g.update_settings(db, user, SettingsUpdate(daily_goal=80), today=BASE)
    profile = db.get(GamificationProfile, user.id)
    profile.xp_total = 95
    db.commit()
    up = read_lesson(db, user, "l1")
    assert up.total_xp == 105
    assert (up.previous_level, up.level, up.level_up) == (1, 2, True)
    assert up.level_title == "Sprout"
    assert up.xp_into_level == 5 and up.xp_for_next_level == 200
    again = read_lesson(db, user, "l2")
    assert (again.previous_level, again.level, again.level_up) == (2, 2, False)


def test_level_badges_unlock_with_the_level(db, user):
    profile = GamificationProfile(user_id=user.id, xp_total=990)
    db.add(profile)
    db.commit()
    r = read_lesson(db, user, "l1")  # 1000 XP: level 5, XP Collector
    ids = {b.id for b in r.new_badges}
    assert {"level-5", "xp-1000", "first-lesson"} <= ids


# --------------------------------------------------------------------------------------
# Module mastery
# --------------------------------------------------------------------------------------


def test_module_is_mastered_when_everything_is_done(db, user):
    assert not g.is_module_complete(db, user.id, MODULE, DETAIL)
    read_lesson(db, user, "l1")
    read_lesson(db, user, "l2")
    submit_code(db, user, "p1")
    submit_code(db, user, "p2")
    quiz = take_quiz(db, user, 100)
    assert "module_complete" not in kinds(quiz)  # p3 is still unsolved
    assert not g.is_module_complete(db, user.id, MODULE, DETAIL)

    last = submit_code(db, user, "p3")
    assert kinds(last)["module_complete"] == 150
    assert g.is_module_complete(db, user.id, MODULE, DETAIL)
    assert "module-1" in [b.id for b in last.new_badges]

    again = submit_code(db, user, "p3")
    assert again.xp_gained == 0
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="module_complete").count() == 1
    assert_ledger_consistent(db, user)


def test_module_needs_a_passing_quiz(db, user):
    for lid in ("l1", "l2"):
        read_lesson(db, user, lid)
    for pid in ("p1", "p2", "p3"):
        submit_code(db, user, pid)
    low = take_quiz(db, user, 60)
    assert "module_complete" not in kinds(low)
    assert not g.is_module_complete(db, user.id, MODULE, DETAIL)

    exactly = take_quiz(db, user, 70)
    assert kinds(exactly)["module_complete"] == 150


def test_finishing_the_last_lesson_completes_the_module(db, user):
    read_lesson(db, user, "l1")
    for pid in ("p1", "p2", "p3"):
        submit_code(db, user, pid)
    take_quiz(db, user, 90)
    last = read_lesson(db, user, "l2")
    assert kinds(last)["module_complete"] == 150


def test_parts_a_module_lacks_are_ignored(db, user):
    lessons_only = make_detail(lessons=("l1", "l2"), problems=(), quiz=False)
    read_lesson(db, user, "l1", detail=lessons_only)
    done = read_lesson(db, user, "l2", detail=lessons_only)
    assert kinds(done)["module_complete"] == 150
    assert g.is_module_complete(db, user.id, MODULE, lessons_only)


def test_an_empty_module_can_never_be_mastered(db, user):
    empty = make_detail(lessons=(), problems=(), quiz=False)
    assert not g.is_module_complete(db, user.id, MODULE, empty)


def test_mastery_uses_the_progress_tables_too(db, user):
    # Progress made before gamification existed still counts towards mastery.
    for lid in ("l1", "l2"):
        db.add(LessonProgress(user_id=user.id, module_id=MODULE, lesson_id=lid))
    for pid in ("p1", "p2", "p3"):
        db.add(CodeSubmission(user_id=user.id, module_id=MODULE, problem_id=pid, code="x", status=SubmissionStatus.PASS))
    db.add(QuizAttempt(user_id=user.id, module_id=MODULE, quiz_id="q", answers={}, score=75, max_score=100, per_question_results=[]))
    db.commit()
    assert g.is_module_complete(db, user.id, MODULE, DETAIL)


def test_five_modules_unlock_halfway_hero_and_ten_unlock_graduate(db, user):
    from app.services.gamification_rules import CORE_MODULE_IDS

    last = None
    for number, module in enumerate(CORE_MODULE_IDS, start=1):
        detail = make_detail(module, lessons=("l1",), problems=(), quiz=False)
        last = read_lesson(db, user, "l1", module=module, detail=detail, on=day(number))
        assert f"module-{number}" in [b.id for b in last.new_badges]
        if number == 5:
            assert "halfway-hero" in [b.id for b in last.new_badges]
    assert "python-graduate" in [b.id for b in last.new_badges]


# --------------------------------------------------------------------------------------
# Badges
# --------------------------------------------------------------------------------------


def test_badges_unlock_once_with_full_info(db, user):
    first = read_lesson(db, user, "l1")
    assert [b.id for b in first.new_badges] == ["first-lesson"]
    badge = first.new_badges[0]
    assert badge.earned is True and badge.earned_at is not None and badge.earned_at.tzinfo is not None
    assert (badge.name, badge.icon, badge.category, badge.rarity) == ("First Steps", "book-open", "learning", "common")
    assert (badge.progress.current, badge.progress.target) == (1, 1)

    second = read_lesson(db, user, "l2")
    assert second.new_badges == []
    assert db.query(UserBadge).filter_by(user_id=user.id, badge_id="first-lesson").count() == 1


def test_badge_catalogue_shows_earned_flags_and_progress(db, user):
    read_lesson(db, user, "l1")
    read_lesson(db, user, "l2")
    badges = g.list_badges(db, user)
    assert len(badges) == 35
    by_id = {b.id: b for b in badges}
    assert by_id["first-lesson"].earned and by_id["first-lesson"].earned_at is not None
    assert not by_id["lessons-10"].earned and by_id["lessons-10"].earned_at is None
    assert (by_id["lessons-10"].progress.current, by_id["lessons-10"].progress.target) == (2, 10)
    assert by_id["first-lesson"].progress.current == 1  # capped at the target
    assert (by_id["streak-3"].progress.current, by_id["streak-3"].progress.target) == (1, 3)


def test_lesson_badges_unlock_at_ten_reads(db, user):
    results = [g.record_lesson_read(db, user, MODULE, f"l{i}", today=BASE) for i in range(10)]
    assert "lessons-10" in [b.id for b in results[-1].new_badges]
    assert all("lessons-10" not in [b.id for b in r.new_badges] for r in results[:-1])


def test_quiz_badges(db, user):
    r = take_quiz(db, user, 85)
    ids = [b.id for b in r.new_badges]
    assert "first-quiz" in ids and "quiz-80" in ids and "perfect-quiz" not in ids
    perfect = take_quiz(db, user, 100)
    assert "perfect-quiz" in [b.id for b in perfect.new_badges]


def test_streak_and_goal_badges(db, user):
    g.update_settings(db, user, SettingsUpdate(daily_goal=20), today=day(0))
    seen = set()
    for i in range(7):
        for part in range(2):  # two lessons a day reaches the 20 XP goal every day
            r = g.record_lesson_read(db, user, MODULE, f"d{i}-{part}", today=day(i))
            seen |= {b.id for b in r.new_badges}
    assert {"streak-3", "streak-7", "goal-getter"} <= seen


def test_listing_badges_does_not_create_rows(db, user):
    g.list_badges(db, user)
    g.get_summary(db, user, today=BASE)
    assert db.query(GamificationProfile).count() == 0
    assert db.query(UserBadge).count() == 0


# --------------------------------------------------------------------------------------
# Generated modules
# --------------------------------------------------------------------------------------


def test_generated_modules_earn_nothing_but_still_count_for_the_streak(db, user):
    db.add(LessonProgress(user_id=user.id, module_id=GENERATED, lesson_id="g1"))
    db.commit()
    lesson = g.record_lesson_read(db, user, GENERATED, "g1", detail=GEN_DETAIL, today=day(0))
    attempt = QuizAttempt(user_id=user.id, module_id=GENERATED, quiz_id="q", answers={}, score=100, max_score=100, per_question_results=[])
    db.add(attempt)
    db.commit()
    quiz = g.record_quiz_attempt(db, user, GENERATED, attempt.id, 100, detail=GEN_DETAIL, today=day(0))
    code = g.record_problem_submission(
        db, user, GENERATED, "gp1", difficulty="hard", passed=True, prior_submissions=0, detail=GEN_DETAIL, today=day(0)
    )
    for r in (lesson, quiz, code):
        assert r.xp_gained == 0 and r.events == [] and r.new_badges == []
        assert r.total_xp == 0 and r.level == 1
        assert r.streak.count == 1 and r.streak.active_today
    assert ledger(db, user) == []
    assert db.query(UserBadge).count() == 0
    db.refresh(user)
    assert user.streak_count == 1

    # the streak still grows from generated-only days
    next_day = g.record_lesson_read(db, user, GENERATED, "g2", detail=GEN_DETAIL, today=day(1))
    assert next_day.streak.count == 2 and next_day.streak.extended


def test_generated_modules_never_complete_and_never_feed_badge_progress(db, user):
    for lid in ("g1", "g2"):
        read_lesson(db, user, lid, module=GENERATED, detail=GEN_DETAIL)
    submit_code(db, user, "gp1", module=GENERATED, detail=GEN_DETAIL)
    take_quiz(db, user, 100, module=GENERATED, detail=GEN_DETAIL)
    assert not g.is_module_complete(db, user.id, GENERATED, GEN_DETAIL)
    badges = {b.id: b for b in g.list_badges(db, user)}
    assert badges["first-lesson"].progress.current == 0
    assert badges["first-solve"].progress.current == 0
    assert badges["first-quiz"].progress.current == 0
    assert not any(b.earned for b in badges.values())


def test_a_milestone_reached_on_a_generated_day_is_paid_by_the_next_core_activity(db, user):
    g.record_lesson_read(db, user, MODULE, "a", today=day(0))
    g.record_lesson_read(db, user, MODULE, "b", today=day(1))
    generated = g.record_lesson_read(db, user, GENERATED, "g1", detail=GEN_DETAIL, today=day(2))
    assert generated.streak.count == 3 and generated.streak.milestone is None and generated.xp_gained == 0
    core = g.record_lesson_read(db, user, MODULE, "c", today=day(2))
    assert core.streak.milestone == 3 and kinds(core)["streak_milestone"] == 15


# --------------------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------------------


def test_summary_for_a_brand_new_learner(db, user):
    s = g.get_summary(db, user, today=BASE)
    assert (s.xp_total, s.level, s.level_title) == (0, 1, "Hatchling")
    assert (s.xp_into_level, s.xp_for_next_level, s.next_level_xp) == (0, 100, 100)
    assert (s.streak.count, s.streak.longest, s.streak.freezes) == (0, 0, 0)
    assert not s.streak.active_today and not s.streak.at_risk
    assert (s.daily.goal, s.daily.xp_today, s.daily.goal_met) == (30, 0, False)
    assert [(p.date, p.xp) for p in s.weekly] == [(day(i).isoformat(), 0) for i in range(-6, 1)]
    assert (s.badges_earned, s.badges_total) == (0, 35)
    assert s.recent_badges == [] and s.recent_events == []
    assert s.show_on_leaderboard is False


def test_summary_weekly_series_is_seven_days_oldest_first_with_gaps_filled(db, user):
    g.update_settings(db, user, SettingsUpdate(daily_goal=80), today=day(0))
    g.record_lesson_read(db, user, MODULE, "a", today=day(0))
    g.record_lesson_read(db, user, MODULE, "b", today=day(0))
    g.record_lesson_read(db, user, MODULE, "c", today=day(2))
    s = g.get_summary(db, user, today=day(3))
    assert [p.date for p in s.weekly] == [day(i).isoformat() for i in range(-3, 4)]
    assert [p.xp for p in s.weekly] == [0, 0, 0, 20, 0, 10, 0]
    old = g.get_summary(db, user, today=day(30))
    assert all(p.xp == 0 for p in old.weekly)


def test_summary_levels_and_totals_match_the_ledger(db, user):
    submit_code(db, user, "p1", difficulty="hard")
    s = g.get_summary(db, user, today=BASE)
    assert s.xp_total == 80  # 60 + 10 first try + 10 daily goal
    assert s.daily.xp_today == 70 and s.daily.goal_met
    assert_ledger_consistent(db, user)


def test_summary_recent_badges_and_events_are_newest_first_and_capped(db, user):
    for i in range(12):
        g.record_lesson_read(db, user, MODULE, f"l{i}", today=day(i))
    s = g.get_summary(db, user, today=day(11))
    assert len(s.recent_events) == 8
    stamps = [e.created_at for e in s.recent_events]
    assert stamps == sorted(stamps, reverse=True)
    assert all(e.amount > 0 for e in s.recent_events)
    assert len(s.recent_badges) <= 4
    earned_at = [b.earned_at for b in s.recent_badges]
    assert earned_at == sorted(earned_at, reverse=True)
    assert all(b.earned and b.progress.current == b.progress.target for b in s.recent_badges)
    assert s.badges_earned >= len(s.recent_badges)


def test_summary_marks_a_streak_at_risk_only_when_yesterday_was_active(db, user):
    g.record_lesson_read(db, user, MODULE, "a", today=day(0))
    g.record_lesson_read(db, user, MODULE, "b", today=day(1))

    today_view = g.get_summary(db, user, today=day(1))
    assert today_view.streak.active_today and not today_view.streak.at_risk and today_view.streak.count == 2

    tomorrow = g.get_summary(db, user, today=day(2))
    assert tomorrow.streak.at_risk and not tomorrow.streak.active_today and tomorrow.streak.count == 2

    lapsed = g.get_summary(db, user, today=day(4))
    assert lapsed.streak.count == 0 and not lapsed.streak.at_risk
    assert lapsed.streak.longest == 2


def test_summary_keeps_the_streak_alive_when_a_freeze_will_cover_yesterday(db, user):
    for i in range(7):
        g.record_lesson_read(db, user, MODULE, f"l{i}", today=day(i))  # earns a freeze
    covered = g.get_summary(db, user, today=day(8))
    assert covered.streak.count == 7 and covered.streak.freezes == 1 and not covered.streak.at_risk
    gone = g.get_summary(db, user, today=day(9))
    assert gone.streak.count == 0


def test_summary_daily_xp_is_zero_on_a_new_day(db, user):
    g.record_lesson_read(db, user, MODULE, "a", today=day(0))
    assert g.get_summary(db, user, today=day(0)).daily.xp_today == 10
    assert g.get_summary(db, user, today=day(1)).daily.xp_today == 0


# --------------------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------------------


def test_settings_reject_goals_outside_the_allowed_set(db, user):
    with pytest.raises(ValidationError):
        SettingsUpdate(daily_goal=25)
    with pytest.raises(ValueError):
        g.update_settings(db, user, SettingsUpdate.model_construct(daily_goal=25))  # bypasses the model validator
    with pytest.raises(ValueError):
        g.update_settings(db, user, {"daily_goal": 99})
    assert db.query(GamificationProfile).count() == 0


@pytest.mark.parametrize("goal", [20, 30, 50, 80])
def test_settings_accept_every_allowed_goal(db, user, goal):
    assert g.update_settings(db, user, SettingsUpdate(daily_goal=goal), today=BASE).daily.goal == goal


def test_settings_are_saved_and_partial_updates_leave_the_rest_alone(db, user):
    s = g.update_settings(db, user, SettingsUpdate(daily_goal=50, show_on_leaderboard=True), today=BASE)
    assert s.daily.goal == 50 and s.show_on_leaderboard is True

    s = g.update_settings(db, user, SettingsUpdate(show_on_leaderboard=False), today=BASE)
    assert s.daily.goal == 50 and s.show_on_leaderboard is False

    s = g.update_settings(db, user, SettingsUpdate(daily_goal=20), today=BASE)
    assert s.daily.goal == 20 and s.show_on_leaderboard is False

    s = g.update_settings(db, user, SettingsUpdate(), today=BASE)
    assert s.daily.goal == 20
    assert g.get_summary(db, user, today=BASE).daily.goal == 20


def test_changing_the_goal_is_not_streak_activity(db, user):
    g.update_settings(db, user, SettingsUpdate(daily_goal=50), today=BASE)
    profile = db.get(GamificationProfile, user.id)
    assert profile.last_active_date is None and ledger(db, user) == []


# --------------------------------------------------------------------------------------
# Leaderboard
# --------------------------------------------------------------------------------------

_seed = itertools.count(1)


def join_board(db, user, *, opted_in=True):
    g.update_settings(db, user, SettingsUpdate(show_on_leaderboard=opted_in), today=BASE)


def give_xp(db, user, amount, *, ago=timedelta(0)):
    """Put XP straight into the ledger, `ago` in the past (the profile must exist)."""
    when = datetime.now(timezone.utc) - ago
    db.add(XPEvent(
        user_id=user.id, kind="lesson", ref_key=f"seed/{next(_seed)}", amount=amount,
        local_date=when.date(), meta={}, created_at=when,
    ))
    db.get(GamificationProfile, user.id).xp_total += amount
    db.commit()


def test_leaderboard_lists_only_opted_in_learners_with_anonymised_names(db):
    asha = make_user(db, name="Asha Kumar")
    bala = make_user(db, name="Bala Venkata Singh")
    shy = make_user(db, name="Shy Person")
    mono = make_user(db, name="Madonna")
    for u, xp in ((asha, 120), (bala, 80), (mono, 40)):
        join_board(db, u)
        give_xp(db, u, xp)
    join_board(db, shy, opted_in=False)
    give_xp(db, shy, 999)

    board = g.get_leaderboard(db, asha)
    assert board.period == "week"
    assert [(e.rank, e.name, e.xp) for e in board.entries] == [(1, "Asha K.", 120), (2, "Bala S.", 80), (3, "Madonna", 40)]
    assert [e.is_me for e in board.entries] == [True, False, False]
    assert all(e.level >= 1 for e in board.entries)
    assert (board.me.rank, board.me.xp, board.me.opted_in) == (1, 120, True)
    flat = board.model_dump_json()
    assert "Kumar" not in flat and "Singh" not in flat and "Shy" not in flat


def test_leaderboard_never_shows_an_email_address(db):
    leaky = make_user(db, name="kid.name@example.com")
    join_board(db, leaky)
    give_xp(db, leaky, 10)
    board = g.get_leaderboard(db, leaky)
    assert board.entries[0].name == "Learner"  # not even the part before the @
    assert "@" not in board.model_dump_json() and "kid" not in board.model_dump_json()


def test_leaderboard_ties_share_the_better_rank_and_are_ordered_by_name(db):
    zed = make_user(db, name="Zed Zebra")  # created first, so it has the lowest id
    amy = make_user(db, name="Amy Adams")
    bob = make_user(db, name="Bob Brown")
    top = make_user(db, name="Top Scorer")
    low = make_user(db, name="Low Scorer")
    for u, xp in ((zed, 100), (amy, 100), (bob, 100), (top, 300), (low, 10)):
        join_board(db, u)
        give_xp(db, u, xp)
    board = g.get_leaderboard(db, low)
    assert [(e.rank, e.name) for e in board.entries] == [
        (1, "Top S."), (2, "Amy A."), (2, "Bob B."), (2, "Zed Z."), (5, "Low S."),
    ]
    assert board.me.rank == 5


def test_leaderboard_is_a_rolling_seven_days_by_created_at(db):
    fresh = make_user(db, name="Fresh Faye")
    stale = make_user(db, name="Stale Sam")
    edge = make_user(db, name="Edge Eli")
    for u in (fresh, stale, edge):
        join_board(db, u)
    give_xp(db, fresh, 50, ago=timedelta(days=1))
    give_xp(db, stale, 500, ago=timedelta(days=7, hours=1))
    give_xp(db, edge, 70, ago=timedelta(days=6, hours=23))
    give_xp(db, edge, 900, ago=timedelta(days=8))  # old XP does not count
    board = g.get_leaderboard(db, fresh)
    assert [(e.name, e.xp) for e in board.entries] == [("Edge E.", 70), ("Fresh F.", 50)]
    assert board.me.xp == 50


def test_leaderboard_shows_the_top_ten_and_the_callers_own_rank(db):
    users = [make_user(db, name=f"Person{chr(65 + n)} Test") for n in range(12)]
    for n, u in enumerate(users):
        join_board(db, u)
        give_xp(db, u, 100 + n)  # PersonL leads, PersonA is last
    board = g.get_leaderboard(db, users[0])
    assert len(board.entries) == 10
    assert [e.rank for e in board.entries] == list(range(1, 11))
    assert board.entries[0].name == "PersonL T."
    assert not any(e.is_me for e in board.entries)
    assert (board.me.rank, board.me.xp, board.me.opted_in) == (12, 100, True)


def test_leaderboard_for_a_learner_who_has_not_opted_in(db):
    me = make_user(db, name="Quiet Quinn")
    other = make_user(db, name="Open Olive")
    join_board(db, other)
    give_xp(db, other, 60)
    join_board(db, me, opted_in=False)
    give_xp(db, me, 500)
    board = g.get_leaderboard(db, me)
    assert [e.name for e in board.entries] == ["Open O."]
    assert (board.me.rank, board.me.xp, board.me.opted_in) == (None, 500, False)


def test_leaderboard_for_a_learner_without_a_profile_is_empty_and_read_only(db):
    me = make_user(db)
    board = g.get_leaderboard(db, me)
    assert board.entries == []
    assert (board.me.rank, board.me.xp, board.me.opted_in) == (None, 0, False)
    assert db.query(GamificationProfile).count() == 0


def test_leaderboard_opted_in_without_xp_this_week_ranks_after_everyone(db):
    me = make_user(db, name="Idle Ida")
    busy = make_user(db, name="Busy Bee")
    for u in (me, busy):
        join_board(db, u)
    give_xp(db, busy, 40)
    give_xp(db, me, 400, ago=timedelta(days=30))
    board = g.get_leaderboard(db, me)
    assert [e.name for e in board.entries] == ["Busy B."]
    assert (board.me.rank, board.me.xp) == (2, 0)


def test_leaderboard_ignores_zero_xp_markers(db):
    me = make_user(db, name="Mark Marker")
    join_board(db, me)
    db.add(XPEvent(user_id=me.id, kind="comeback", ref_key="2026-03-02", amount=0, local_date=BASE, meta={}))
    db.commit()
    assert g.get_leaderboard(db, me).entries == []


# --------------------------------------------------------------------------------------
# get_tz_offset
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("-330", -330), ("330", 330), ("+120", 120), (" 60 ", 60), ("0", 0),
        ("840", 840), ("841", 840), ("99999", 840), ("-841", -840), ("-99999", -840),
        (None, 0), ("", 0), ("abc", 0), ("5.5", 0), ("1e3", 0), ("NaN", 0), ("9" * 5000, 0),
    ],
)
def test_get_tz_offset_parses_clamps_and_never_raises(raw, expected):
    assert get_tz_offset(raw) == expected


# --------------------------------------------------------------------------------------
# HTTP layer
# --------------------------------------------------------------------------------------


@pytest.fixture
def client(db):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


def login_as(user):
    app.dependency_overrides[get_current_user] = lambda: user


def test_endpoints_require_login(client):
    for method, path in (("get", "/api/gamification/me"), ("get", "/api/gamification/badges"),
                         ("get", "/api/gamification/leaderboard"), ("patch", "/api/gamification/settings")):
        assert getattr(client, method)(path).status_code == 401, path


def test_me_returns_the_summary_contract(client, db, user):
    login_as(user)
    g.record_lesson_read(db, user, MODULE, "l1", today=g.local_today(0))
    r = client.get("/api/gamification/me")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {
        "xp_total", "level", "level_title", "xp_into_level", "xp_for_next_level", "next_level_xp",
        "streak", "daily", "weekly", "badges_earned", "badges_total", "recent_badges",
        "recent_events", "show_on_leaderboard",
    }
    assert set(body["streak"]) == {
        "count", "longest", "freezes", "extended", "used_freeze", "milestone", "broken_from", "active_today", "at_risk",
    }
    assert set(body["daily"]) == {"goal", "xp_today", "goal_met", "just_met"}
    assert body["xp_total"] == 10 and len(body["weekly"]) == 7
    assert body["recent_badges"][0]["id"] == "first-lesson"
    assert body["recent_badges"][0]["earned_at"].endswith("Z") or "+00:00" in body["recent_badges"][0]["earned_at"]


def test_me_uses_the_tz_offset_header_for_the_local_date(client, db, user):
    login_as(user)
    expected = g.local_today(-840).isoformat()
    body = client.get("/api/gamification/me", headers={"X-TZ-Offset": "-840"}).json()
    assert body["weekly"][-1]["date"] == expected
    garbage = client.get("/api/gamification/me", headers={"X-TZ-Offset": "not-a-number"})
    assert garbage.status_code == 200
    assert garbage.json()["weekly"][-1]["date"] == g.local_today(0).isoformat()


def test_badges_endpoint_lists_the_whole_catalogue(client, db, user):
    login_as(user)
    r = client.get("/api/gamification/badges")
    assert r.status_code == 200
    badges = r.json()["badges"]
    assert len(badges) == 35
    assert set(badges[0]) == {"id", "name", "description", "icon", "category", "rarity", "earned", "earned_at", "progress"}
    assert all(b["earned"] is False and b["earned_at"] is None for b in badges)


def test_leaderboard_endpoint(client, db, user):
    login_as(user)
    body = client.get("/api/gamification/leaderboard").json()
    assert body == {"period": "week", "entries": [], "me": {"rank": None, "xp": 0, "opted_in": False}}


def test_settings_endpoint_updates_and_validates(client, db, user):
    login_as(user)
    ok = client.patch("/api/gamification/settings", json={"daily_goal": 50, "show_on_leaderboard": True})
    assert ok.status_code == 200
    assert ok.json()["daily"]["goal"] == 50 and ok.json()["show_on_leaderboard"] is True
    assert client.get("/api/gamification/me").json()["daily"]["goal"] == 50

    bad = client.patch("/api/gamification/settings", json={"daily_goal": 25})
    assert bad.status_code == 422
    assert client.get("/api/gamification/me").json()["daily"]["goal"] == 50  # unchanged

    assert client.patch("/api/gamification/settings", json={"show_on_leaderboard": "maybe"}).status_code == 422
    assert client.patch("/api/gamification/settings", json={}).status_code == 200


# --------------------------------------------------------------------------------------
# Hardening (review round 1)
# --------------------------------------------------------------------------------------

UTC = timezone.utc
T0 = datetime(2026, 3, 2, 9, 0, tzinfo=UTC)


def real_cooldowns(monkeypatch):
    """Put the real anti-farming guards back (the autouse fixture switches them off)."""
    from app.services import gamification_rules as rules

    monkeypatch.setattr(g, "QUIZ_RETRY_COOLDOWN", rules.QUIZ_RETRY_COOLDOWN)
    monkeypatch.setattr(g, "LESSON_MIN_GAP", rules.LESSON_MIN_GAP)


def paid(db, user, kind):
    return db.query(XPEvent).filter_by(user_id=user.id, kind=kind).count()


# ---- R1-1: quiz rewards cannot be farmed by replaying the answer key ---------------------


def test_a_quiz_retaken_straight_after_seeing_the_answers_pays_nothing(db, user, monkeypatch):
    real_cooldowns(monkeypatch)
    blank = take_quiz(db, user, 0, at=T0)
    assert blank.xp_gained == 0 and [b.id for b in blank.new_badges] == ["first-quiz"]

    cheat = take_quiz(db, user, 100, at=T0 + timedelta(minutes=1))  # the answers were just revealed
    assert cheat.xp_gained == 0 and cheat.events == [] and cheat.new_badges == []
    assert paid(db, user, "quiz") == paid(db, user, "quiz_perfect") == 0
    assert {b.id for b in g.list_badges(db, user) if b.earned} == {"first-quiz"}
    assert g.list_badges(db, user)[5].progress.current == 0  # quiz-80 (Sharp Mind) is not unlocked either
    assert cheat.streak.count == 1  # it still counts as learning activity

    honest = take_quiz(db, user, 100, at=T0 + timedelta(hours=13))  # a real retake, after sleeping on it
    assert (kinds(honest)["quiz"], kinds(honest)["quiz_perfect"]) == (50, 25)
    assert {"quiz-80", "perfect-quiz"} <= {b.id for b in honest.new_badges}
    assert_ledger_consistent(db, user)


def test_the_first_attempt_always_pays_and_a_spaced_retake_pays_the_improvement(db, user, monkeypatch):
    real_cooldowns(monkeypatch)
    assert kinds(take_quiz(db, user, 40, at=T0)) == {"quiz": 20}
    retake = take_quiz(db, user, 80, at=T0 + timedelta(hours=12))  # exactly the cooldown later
    assert kinds(retake)["quiz"] == 20


def test_hammering_the_quiz_keeps_the_learner_on_cooldown(db, user, monkeypatch):
    real_cooldowns(monkeypatch)
    take_quiz(db, user, 0, at=T0)
    take_quiz(db, user, 0, at=T0 + timedelta(hours=6))
    third = take_quiz(db, user, 100, at=T0 + timedelta(hours=11, minutes=59))  # 12h after the first, not the second
    assert third.xp_gained == 0
    assert kinds(take_quiz(db, user, 100, at=T0 + timedelta(hours=24))) == {"quiz": 50, "quiz_perfect": 25, "daily_goal": 10}


def test_a_quiz_cheated_within_the_cooldown_does_not_master_the_module(db, user, monkeypatch):
    real_cooldowns(monkeypatch)
    for lid in ("l1", "l2"):  # read long before gamification started for this learner
        db.add(LessonProgress(user_id=user.id, module_id=MODULE, lesson_id=lid, viewed_at=T0 - timedelta(days=30)))
    for pid in ("p1", "p2", "p3"):
        submit_code(db, user, pid)
    db.commit()
    take_quiz(db, user, 0, at=T0)
    cheat = take_quiz(db, user, 100, at=T0 + timedelta(seconds=30))
    assert "module_complete" not in kinds(cheat) and not g.is_module_complete(db, user.id, MODULE, DETAIL)
    done = take_quiz(db, user, 100, at=T0 + timedelta(days=1))
    assert kinds(done)["module_complete"] == 150


def test_quiz_cooldowns_are_per_module(db, user, monkeypatch):
    real_cooldowns(monkeypatch)
    other = make_detail("module-2-operators-decision-making")
    take_quiz(db, user, 100, at=T0)
    second = take_quiz(db, user, 100, at=T0 + timedelta(minutes=1), module=other.id, detail=other)
    assert kinds(second)["quiz"] == 50


# ---- R1-3: the local date cannot be forged ------------------------------------------------


def test_a_changed_offset_is_only_believed_after_the_cooldown(db, user):
    now = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)
    profile = g._new_profile(user.id)
    assert g._resolve_offset(profile, -330, now) == (-330, True)  # the first offset is taken
    profile.tz_offset, profile.tz_changed_at = -330, now
    assert g._resolve_offset(profile, -330, now + timedelta(days=9)) == (-330, False)
    assert g._resolve_offset(profile, 840, now + timedelta(hours=1)) == (-330, False)  # too soon: ignored
    assert g._resolve_offset(profile, 840, now + timedelta(hours=7)) == (840, True)
    assert g._resolve_offset(profile, 99999, now + timedelta(hours=7)) == (840, True)  # clamped like everywhere else


def test_the_effective_date_is_never_earlier_than_the_last_activity(db, user):
    g.record_lesson_read(db, user, MODULE, "l1", today=day(5))
    again = g.record_lesson_read(db, user, MODULE, "l2", today=day(3))  # a clock that went backwards
    assert again.daily.xp_today == 20 and again.streak.extended is False
    assert {e.local_date for e in ledger(db, user)} == {day(5)}
    assert g.get_summary(db, user, today=day(3)).daily.xp_today == 20


# ---- R1-5: lessons cannot be farmed with an instant loop ----------------------------------


def test_lessons_read_faster_than_anyone_can_read_pay_nothing_until_read_again(db, user, monkeypatch):
    real_cooldowns(monkeypatch)
    results = [read_lesson(db, user, lid, detail=make_detail(lessons=("l1", "l2", "l3"))) for lid in ("l1", "l2", "l3")]
    assert [r.xp_gained for r in results] == [10, 0, 0]  # the bulk 'reads' are not paid...
    assert g.list_badges(db, user)[0].progress.current == 1  # ...and do not count as reads for the badges
    assert results[1].streak.count == 1  # (they are still streak activity)

    # A real reader who takes their time is paid in full: move the paid lesson back in time and read l2 again.
    for event in db.query(XPEvent).filter_by(user_id=user.id, kind="lesson"):
        event.created_at = datetime.now(UTC) - timedelta(minutes=2)
    db.commit()
    assert read_lesson(db, user, "l2", detail=make_detail(lessons=("l1", "l2", "l3"))).xp_gained == 10


def test_paced_lesson_views_pay_no_xp_but_still_count_as_read(db, user, monkeypatch):
    real_cooldowns(monkeypatch)
    lessons_only = make_detail(lessons=("l1", "l2"), problems=(), quiz=False)
    read_lesson(db, user, "l1", detail=lessons_only)
    rushed = read_lesson(db, user, "l2", detail=lessons_only)
    assert rushed.xp_gained == 0 or "lesson" not in kinds(rushed)  # the second lesson paid no lesson XP
    assert g.is_module_complete(db, user.id, MODULE, lessons_only)  # but it is read, as the UI says


def test_lessons_read_before_gamification_started_still_count(db, user, monkeypatch):
    real_cooldowns(monkeypatch)
    for lid in ("l1", "l2"):
        db.add(LessonProgress(user_id=user.id, module_id=MODULE, lesson_id=lid))
    db.commit()
    lessons_only = make_detail(lessons=("l1", "l2"), problems=(), quiz=False)
    assert g.is_module_complete(db, user.id, MODULE, lessons_only)  # no profile yet: all of it is earlier progress


# ---- R1-6 / R1-7: a legacy streak ---------------------------------------------------------


def legacy(db, user, count, days_ago=1):
    user.streak_count = count
    user.last_streak_update = datetime(2026, 3, 2, 12, 0, tzinfo=UTC) - timedelta(days=days_ago)
    db.commit()


def test_the_summary_shows_a_legacy_streak_before_the_first_activity_and_creates_nothing(db, user):
    legacy(db, user, 12, days_ago=1)
    summary = g.get_summary(db, user, today=day(0))
    assert (summary.streak.count, summary.streak.at_risk, summary.streak.active_today) == (12, True, False)
    assert summary.streak.longest == 12
    assert db.query(GamificationProfile).count() == 0 and db.query(XPEvent).count() == 0

    legacy(db, user, 5, days_ago=0)
    today = g.get_summary(db, user, today=day(0)).streak
    assert (today.count, today.active_today, today.at_risk) == (5, True, False)

    legacy(db, user, 12, days_ago=3)
    assert g.get_summary(db, user, today=day(0)).streak.count == 0  # lapsed long ago: nothing to show
    assert db.query(GamificationProfile).count() == 0


def test_the_summary_and_the_first_activity_agree_about_a_legacy_streak(db, user):
    legacy(db, user, 12, days_ago=1)
    before = g.get_summary(db, user, today=day(0)).streak.count
    after = g.record_lesson_read(db, user, MODULE, "l1", today=day(0)).streak
    assert (before, after.count, after.extended) == (12, 13, True)
    assert g.get_summary(db, user, today=day(0)).streak.count == 13


def test_a_legacy_badge_list_is_read_only_too(db, user):
    legacy(db, user, 12, days_ago=1)
    assert not any(b.earned for b in g.list_badges(db, user))
    assert db.query(GamificationProfile).count() == 0


@pytest.mark.parametrize("carried", [3, 7, 14, 30, 60, 100])
def test_a_legacy_streak_earns_no_milestone_xp_or_streak_badges_on_the_first_activity(db, user, carried):
    legacy(db, user, carried, days_ago=0)  # bumped today under the old rules: lands exactly on a milestone
    first = g.record_lesson_read(db, user, MODULE, "l1", today=day(0))
    assert kinds(first) == {"lesson": 10} and first.streak.milestone is None
    assert first.streak.count == carried and first.streak.extended is False
    assert [b.id for b in first.new_badges] == ["first-lesson"]  # no streak-3 / streak-7 / streak-30 yet
    assert first.streak.longest == carried  # (shown as the streak the learner has)
    assert paid(db, user, "streak_milestone") == len([d for d in g.STREAK_MILESTONES if d <= carried])
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="streak_milestone").filter(XPEvent.amount > 0).count() == 0
    assert_ledger_consistent(db, user)


def test_a_carried_streak_keeps_counting_and_later_milestones_still_pay(db, user):
    legacy(db, user, 5, days_ago=1)
    for n, expected in ((0, 6), (1, 7)):  # the 7th day is a real, earned milestone
        r = g.record_lesson_read(db, user, MODULE, f"l{n}", today=day(n))
        assert r.streak.count == expected
    assert r.streak.milestone == 7 and kinds(r)["streak_milestone"] == 50


# ---- R1-11: lowering the daily goal ------------------------------------------------------


def test_lowering_the_goal_below_todays_xp_pays_the_bonus_once(db, user):
    g.update_settings(db, user, SettingsUpdate(daily_goal=80), today=day(0))
    for lid in ("a1", "a2", "a3"):
        g.record_lesson_read(db, user, MODULE, lid, today=day(0))
    assert paid(db, user, "daily_goal") == 0

    lowered = g.update_settings(db, user, SettingsUpdate(daily_goal=20), today=day(0))
    assert (lowered.daily.goal, lowered.daily.xp_today, lowered.daily.goal_met) == (20, 30, True)
    assert paid(db, user, "daily_goal") == 1 and lowered.xp_total == 40  # the bonus is really there
    assert "goal-getter" not in {b.id for b in lowered.recent_badges}

    g.update_settings(db, user, SettingsUpdate(daily_goal=20), today=day(0))  # again: idempotent
    g.update_settings(db, user, SettingsUpdate(daily_goal=30), today=day(0))
    g.update_settings(db, user, SettingsUpdate(daily_goal=50), today=day(0))  # raised: never a second bonus
    g.record_lesson_read(db, user, MODULE, "a4", today=day(0))
    g.record_lesson_read(db, user, MODULE, "a5", today=day(0))
    assert paid(db, user, "daily_goal") == 1
    assert_ledger_consistent(db, user)


def test_lowering_the_goal_does_not_pay_when_the_day_is_not_done_yet(db, user):
    g.record_lesson_read(db, user, MODULE, "a1", today=day(0))
    g.update_settings(db, user, SettingsUpdate(daily_goal=20), today=day(0))
    assert paid(db, user, "daily_goal") == 0
    assert g.record_lesson_read(db, user, MODULE, "a2", today=day(0)).daily.just_met is True


def test_a_goal_met_yesterday_is_not_paid_today(db, user):
    g.update_settings(db, user, SettingsUpdate(daily_goal=20), today=day(0))
    for lid in ("a1", "a2"):
        g.record_lesson_read(db, user, MODULE, lid, today=day(0))
    g.update_settings(db, user, SettingsUpdate(daily_goal=80), today=day(1))
    assert paid(db, user, "daily_goal") == 1  # day 0's, and nothing new for the fresh day 1


# ---- R1-12: idle calls skip the badge statistics -----------------------------------------


def test_re_reading_a_lesson_skips_the_badge_statistics(db, user, monkeypatch):
    read_lesson(db, user, "l1")
    read_lesson(db, user, "l2")
    queries = []
    listener = lambda conn, cursor, statement, *a: queries.append(statement)
    event.listen(db.get_bind(), "before_cursor_execute", listener)
    try:
        monkeypatch.setattr(g, "_collect_stats", lambda *a, **k: (_ for _ in ()).throw(AssertionError("stats ran")))
        again = read_lesson(db, user, "l1")  # nothing changes: no XP, same day
        assert again.xp_gained == 0 and again.streak.extended is False
    finally:
        event.remove(db.get_bind(), "before_cursor_execute", listener)
    assert len(queries) < 15


def test_a_new_day_still_evaluates_badges_even_without_xp(db, user):
    for n in range(2):
        g.record_lesson_read(db, user, MODULE, f"l{n}", today=day(n))
    third = g.record_lesson_read(db, user, MODULE, "l0", today=day(2))  # a re-read, but it lights day 3
    assert third.xp_gained == 15 and "streak-3" in {b.id for b in third.new_badges}


# ---- R1-8: names ----------------------------------------------------------------------------


def test_the_leaderboard_never_shows_an_overlong_or_personal_name(db):
    giant = make_user(db, name="B" * 100_000)
    phone = make_user(db, name="9876543210")
    mail = make_user(db, name="Ravi Kumar (ravi@school.edu)")
    for u in (giant, phone, mail):
        join_board(db, u)
        give_xp(db, u, 10)
    board = g.get_leaderboard(db, giant)
    assert sorted(e.name for e in board.entries) == sorted(["B" * 15, "Learner", "Ravi K."])
    dumped = board.model_dump_json()
    assert "9876543210" not in dumped and "school" not in dumped and len(dumped) < 600


def test_signup_names_are_trimmed_and_bounded():
    from app.schemas.auth import SignupRequest

    ok = SignupRequest(email="a@example.com", password="x", full_name="  Asha \n  Kumar ")
    assert ok.full_name == "Asha Kumar"
    for bad in ("", "   ", "B" * 101):
        with pytest.raises(ValidationError):
            SignupRequest(email="a@example.com", password="x", full_name=bad)


# ---- R1-9: leaderboard in SQL -----------------------------------------------------------------


def test_the_weekly_leaderboard_has_an_index_on_created_at():
    assert any([c.name for c in i.columns] == ["created_at"] for i in XPEvent.__table__.indexes)


def test_a_tie_at_tenth_place_is_resolved_by_name_and_ranks_stay_shared(db):
    users = [make_user(db, name=f"Tied {chr(65 + n)}") for n in range(13)]
    for u in users:
        join_board(db, u)
        give_xp(db, u, 50)
    top = make_user(db, name="Zoe Top")
    join_board(db, top)
    give_xp(db, top, 500)
    board = g.get_leaderboard(db, users[12])  # "Tied M": sorted 13th of the tie, outside the shown ten
    assert [e.name for e in board.entries] == ["Zoe T."] + [f"Tied {chr(65 + n)}." for n in range(9)]
    assert [e.rank for e in board.entries] == [1] + [2] * 9
    assert (board.me.rank, board.me.xp) == (2, 50)


def test_the_leaderboard_loads_only_the_learners_that_can_make_the_top_ten(db, monkeypatch):
    users = [make_user(db, name=f"Racer {chr(65 + n)}") for n in range(30)]
    for n, u in enumerate(users):
        join_board(db, u)
        give_xp(db, u, 10 + n)
    loaded = []
    real = g.anonymise_name
    monkeypatch.setattr(g, "anonymise_name", lambda name: loaded.append(name) or real(name))
    board = g.get_leaderboard(db, users[0])
    assert [e.xp for e in board.entries] == [39 - n for n in range(10)]
    assert board.me.rank == 30
    assert len(loaded) == 10  # 30 opted-in learners, but only the ten that can make the board were loaded


def test_the_migration_history_has_a_single_head():
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "alembic"))
    assert ScriptDirectory.from_config(cfg).get_heads() == ["e8a2b3c4d5f6"]


# ---- R1-13: settings are strict -----------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        {"dailyGoal": 50},
        {"daily_goal": "50"},
        {"daily_goal": 50.0},
        {"daily_goal": True},
        {"show_on_leaderboard": "yes"},
        {"show_on_leaderboard": 1},
        {"daily_goal": 50, "extra": 1},
    ],
)
def test_settings_reject_unknown_keys_and_coerced_values(client, db, user, body):
    login_as(user)
    assert client.patch("/api/gamification/settings", json=body).status_code == 422
    assert db.query(GamificationProfile).count() == 0  # and nothing was saved or created


def test_settings_still_accept_exact_values_and_an_empty_body(client, db, user):
    login_as(user)
    assert client.patch("/api/gamification/settings", json={}).status_code == 200
    assert client.patch("/api/gamification/settings", json={"daily_goal": None}).status_code == 422
    r = client.patch("/api/gamification/settings", json={"daily_goal": 80, "show_on_leaderboard": False})
    assert r.status_code == 200 and r.json()["daily"]["goal"] == 80


def test_the_service_revalidates_loose_settings_too(db, user):
    with pytest.raises(ValidationError):
        g.update_settings(db, user, {"daily_goal": "50"})
    with pytest.raises(ValidationError):
        g.update_settings(db, user, {"dailyGoal": 50})
