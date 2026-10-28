"""
Gamification rules: every constant and every pure function (no database, no I/O).

See GAMIFICATION.md at the repository root. The database-facing logic lives in
app/services/gamification.py; keeping the rules here makes them trivial to unit test.
"""
import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Dict, NamedTuple, Optional, Tuple

from app.schemas.gamification import ALLOWED_DAILY_GOALS

# --------------------------------------------------------------------------------------
# XP amounts
# --------------------------------------------------------------------------------------

XP_LESSON = 10
XP_QUIZ_MAX = 50  # a 100% quiz is worth this much in total (awarded as deltas)
XP_QUIZ_PERFECT = 25
XP_PROBLEM_BY_DIFFICULTY: Dict[str, int] = {"easy": 20, "medium": 35, "hard": 60}
XP_FIRST_TRY = 10
XP_MODULE_COMPLETE = 150
XP_DAILY_GOAL = 10

MODULE_QUIZ_PASS_PCT = 70  # best quiz % needed for a module to count as mastered

# Anti-farming guards (server-side, so a script cannot talk its way past them).
#  * The quiz answer key is shown after every submit, so an attempt only pays (quiz XP, the perfect
#    bonus, mastery and the quiz badges) when it is the learner's first one for the module or comes
#    at least this long after their previous attempt: submit-blank-then-resubmit-the-answers earns nothing.
QUIZ_RETRY_COOLDOWN = timedelta(hours=12)
#  * A lesson only pays when at least this long has passed since the learner's previous paid lesson
#    (a real lesson takes minutes to read; a script can fire hundreds of requests per second).
LESSON_MIN_GAP = timedelta(seconds=20)
#  * A changed UTC offset is only believed this long after the previous change, and the local date
#    never moves backwards, so the X-TZ-Offset header cannot be used to mint extra days.
TZ_CHANGE_COOLDOWN = timedelta(hours=6)

# Modules whose id starts with this prefix (AI / faculty made) earn no XP or badges.
GENERATED_MODULE_PREFIX = "generated-"

# Streak length -> one-off bonus XP
STREAK_MILESTONES: Dict[int, int] = {3: 15, 7: 50, 14: 100, 30: 250, 60: 500, 100: 1000}
FREEZE_EVERY_DAYS = 7  # one freeze is earned each time the streak reaches a multiple of this
MAX_FREEZES = 2
COMEBACK_GAP_DAYS = 7  # a gap this long (or longer) records a comeback marker

DEFAULT_DAILY_GOAL = 30
DAILY_GOAL_CHOICES: Tuple[int, ...] = tuple(ALLOWED_DAILY_GOALS)

MAX_LEVEL = 99

# Highest threshold <= level wins.
LEVEL_TITLES: Tuple[Tuple[int, str], ...] = (
    (1, "Hatchling"),
    (2, "Sprout"),
    (3, "Apprentice"),
    (4, "Bug Hunter"),
    (5, "Loop Rider"),
    (6, "Function Fan"),
    (7, "Class Act"),
    (8, "Data Explorer"),
    (9, "Automator"),
    (10, "Python Pro"),
    (12, "Code Wizard"),
    (15, "Grand Master"),
    (20, "Legend"),
)

# XP ledger kinds (xp_events.kind)
KIND_LESSON = "lesson"
KIND_QUIZ = "quiz"
KIND_QUIZ_PERFECT = "quiz_perfect"
KIND_PROBLEM = "problem"
KIND_FIRST_TRY = "problem_first_try"
KIND_MODULE_COMPLETE = "module_complete"
KIND_DAILY_GOAL = "daily_goal"
KIND_STREAK_MILESTONE = "streak_milestone"
KIND_COMEBACK = "comeback"  # amount 0: a marker used by the Comeback Kid badge

EVENT_LABELS: Dict[str, str] = {
    KIND_LESSON: "Lesson read",
    KIND_QUIZ: "Quiz score",
    KIND_QUIZ_PERFECT: "Perfect quiz",
    KIND_PROBLEM: "Problem solved",
    KIND_FIRST_TRY: "First-try solve",
    KIND_MODULE_COMPLETE: "Module mastered",
    KIND_DAILY_GOAL: "Daily goal reached",
    KIND_STREAK_MILESTONE: "Streak bonus",
    KIND_COMEBACK: "Welcome back",
}


def event_label(kind: str, ref_key: Optional[str] = None) -> str:
    """Human readable label for a ledger event, e.g. 'Lesson read' or '7-day streak'."""
    if kind == KIND_STREAK_MILESTONE and ref_key and ref_key.isdigit():
        return f"{ref_key}-day streak"
    return EVENT_LABELS.get(kind, kind.replace("_", " ").capitalize())


# --------------------------------------------------------------------------------------
# Levels
# --------------------------------------------------------------------------------------


def xp_for_level(level: int) -> int:
    """Cumulative XP at which `level` starts: L1 = 0, L2 = 100, L3 = 300, L10 = 4500, L20 = 19000."""
    return 50 * level * (level - 1)


def level_for_xp(xp: int) -> int:
    """The level a learner with `xp` total XP is on (1..MAX_LEVEL)."""
    if xp <= 0:
        return 1
    # Largest L with 50*L*(L-1) <= xp  <=>  L*(L-1) <= xp // 50  <=>  L = (1 + isqrt(1 + 4n)) // 2
    n = int(xp) // 50
    level = (1 + math.isqrt(1 + 4 * n)) // 2
    return max(1, min(MAX_LEVEL, level))


def level_title(level: int) -> str:
    title = LEVEL_TITLES[0][1]
    for threshold, name in LEVEL_TITLES:
        if level >= threshold:
            title = name
    return title


class LevelProgress(NamedTuple):
    level: int
    title: str
    xp_into_level: int  # XP earned inside the current level
    xp_for_next_level: int  # size of the whole current level (denominator of the progress bar)
    next_level_xp: int  # cumulative XP at which the next level starts


def level_progress(xp: int) -> LevelProgress:
    level = level_for_xp(xp)
    start = xp_for_level(level)
    nxt = xp_for_level(level + 1)
    span = nxt - start
    into = max(0, int(xp) - start)
    if level >= MAX_LEVEL:
        into = min(into, span)  # keep the bar at 100% once the cap is reached
    return LevelProgress(level, level_title(level), into, span, nxt)


# --------------------------------------------------------------------------------------
# XP for quizzes and problems
# --------------------------------------------------------------------------------------


def quiz_target_xp(best_pct: float) -> int:
    """Total quiz XP a module is worth for a best score of `best_pct` percent (round half up)."""
    pct = float(best_pct)
    if not math.isfinite(pct):
        return 0
    pct = max(0.0, min(100.0, pct))
    return int(math.floor(XP_QUIZ_MAX * pct / 100 + 0.5))


def problem_xp(difficulty: Optional[str]) -> int:
    """XP for a first solve; unknown difficulties are treated as easy."""
    key = (difficulty or "easy").strip().lower()
    return XP_PROBLEM_BY_DIFFICULTY.get(key, XP_PROBLEM_BY_DIFFICULTY["easy"])


def normalise_difficulty(difficulty: Optional[str]) -> str:
    key = (difficulty or "easy").strip().lower()
    return key if key in XP_PROBLEM_BY_DIFFICULTY else "easy"


def streak_milestone_xp(days: int) -> int:
    return STREAK_MILESTONES.get(days, 0)


# --------------------------------------------------------------------------------------
# Streaks
# --------------------------------------------------------------------------------------


class StreakResult(NamedTuple):
    count: int
    freezes: int
    longest: int
    extended: bool  # first activity of a new local day (the streak flame was lit today)
    used_freeze: bool  # a freeze was spent to bridge a missed day
    broken_from: Optional[int]  # old count when the streak restarted (only if the old count was > 1)
    comeback: bool  # the gap was COMEBACK_GAP_DAYS or more
    milestone: Optional[int]  # milestone day number if `count` just reached one


def compute_streak(
    last_active_date: Optional[date],
    today: date,
    count: int,
    freezes: int,
    longest: int,
) -> StreakResult:
    """
    Advance a streak for one qualifying activity on local date `today`.

    | last_active_date            | result                                                  |
    |-----------------------------|---------------------------------------------------------|
    | None                        | count = 1                                               |
    | today <= last (same day or  | unchanged, extended = False                             |
    |   clock skew)               |                                                         |
    | today - last = 1 day        | count + 1                                               |
    | today - last = 2, freezes>0 | freeze spent, count + 1                                 |
    | otherwise                   | broken_from = old count (if > 1), count = 1             |

    A gap of COMEBACK_GAP_DAYS or more also sets `comeback`. Reaching a multiple of 7 by moving
    forward earns one freeze (max MAX_FREEZES). `longest` is max(longest, count).
    """
    count = max(0, int(count))
    freezes = max(0, int(freezes))
    longest = max(0, int(longest))
    used_freeze = False
    broken_from: Optional[int] = None
    comeback = False
    advanced = False  # moved forward via +1 (the only way to reach a multiple of 7)

    if last_active_date is None:
        new_count = 1
        extended = True
    else:
        gap = (today - last_active_date).days
        if gap <= 0:
            # Same day, or the learner's clock/timezone moved backwards: never punish that.
            return StreakResult(max(count, 1), freezes, max(longest, count, 1), False, False, None, False, None)
        if gap == 1:
            new_count, advanced = count + 1, True
        elif gap == 2 and freezes > 0:
            new_count, advanced = count + 1, True
            freezes -= 1
            used_freeze = True
        else:
            broken_from = count if count > 1 else None
            new_count = 1
            comeback = gap >= COMEBACK_GAP_DAYS
        extended = True

    if advanced and new_count % FREEZE_EVERY_DAYS == 0:
        freezes = min(MAX_FREEZES, freezes + 1)

    milestone = new_count if (advanced and new_count in STREAK_MILESTONES) else None
    return StreakResult(
        count=new_count,
        freezes=freezes,
        longest=max(longest, new_count),
        extended=extended,
        used_freeze=used_freeze,
        broken_from=broken_from,
        comeback=comeback,
        milestone=milestone,
    )


# --------------------------------------------------------------------------------------
# Names
# --------------------------------------------------------------------------------------


MAX_DISPLAY_NAME = 15  # characters of the first name that are ever shown on the leaderboard
_NAME_PUNCTUATION = "'\u2019-"  # apostrophes and hyphens are fine inside a name


def _name_token(token: str) -> Optional[str]:
    """The token as a safe name part, or None when it does not look like a name (digits, '@', symbols ...)."""
    token = token.strip(",.;:")
    if not token or not any(ch.isalpha() for ch in token):
        return None
    if not all(ch.isalpha() or ch in _NAME_PUNCTUATION for ch in token):
        return None
    return token


def anonymise_name(full_name: Optional[str]) -> str:
    """
    'Asha Kumar' -> 'Asha K.'; a single plain name stays as is (capped at MAX_DISPLAY_NAME characters).

    Only letter-only words count: anything with digits, '@' or symbols (an e-mail address, a phone
    number, a username) is dropped and never echoed. 'Learner' is used when nothing usable is left.
    """
    tokens = [t for t in (_name_token(raw) for raw in (full_name or "").split()) if t]
    if not tokens:
        return "Learner"
    first = tokens[0][:MAX_DISPLAY_NAME]
    if len(tokens) == 1:
        return first
    return f"{first} {tokens[-1][0].upper()}."


# --------------------------------------------------------------------------------------
# Badge catalogue
# --------------------------------------------------------------------------------------

# The ten core modules, in curriculum order (ids are the content folder names).
CORE_MODULE_IDS: Tuple[str, ...] = (
    "module-1-introduction-to-python",
    "module-2-operators-decision-making",
    "module-3-loops-pattern-programming",
    "module-4-strings-data-structures",
    "module-5-functions-modular",
    "module-6-file-exception-handling",
    "module-7-oop",
    "module-8-libraries-automation",
    "module-9-data-science",
    "module-10-mini-projects",
)

# (badge name, icon key) for each core module, in the same order as CORE_MODULE_IDS.
_MODULE_BADGES: Tuple[Tuple[str, str], ...] = (
    ("Pythonista", "terminal"),
    ("Decision Maker", "git-branch"),
    ("Loop Legend", "repeat"),
    ("Data Wrangler", "package"),
    ("Function Fan", "square-function"),
    ("File Detective", "folder-search"),
    ("Object Architect", "blocks"),
    ("Automator", "bot"),
    ("Data Scientist", "chart-column"),
    ("Project Builder", "hammer"),
)


@dataclass(frozen=True)
class BadgeDef:
    id: str
    name: str
    description: str
    icon: str  # kebab-case icon key, one of the ICONS keys in frontend/src/lib/icons.tsx (never an emoji)
    category: str  # learning | quizzes | coding | streaks | modules | levels
    rarity: str  # common | rare | epic | legendary
    target: int
    current: Callable[[dict], int]  # stats snapshot -> current value (uncapped)

    def is_earned(self, stats: dict) -> bool:
        return self.current(stats) >= self.target


def _stat(key: str) -> Callable[[dict], int]:
    return lambda stats: int(stats.get(key, 0) or 0)


def _module_done(module_id: str) -> Callable[[dict], int]:
    return lambda stats: 1 if module_id in (stats.get("completed_modules") or ()) else 0


def _badge(id, name, description, icon, category, rarity, target, stat_key) -> BadgeDef:
    return BadgeDef(id, name, description, icon, category, rarity, target, _stat(stat_key))


def _build_catalogue() -> Tuple[BadgeDef, ...]:
    badges = [
        _badge("first-lesson", "First Steps", "Read your first lesson.", "book-open", "learning", "common", 1, "lessons_read"),
        _badge("lessons-10", "Bookworm", "Read 10 lessons.", "library", "learning", "common", 10, "lessons_read"),
        _badge("lessons-30", "Scholar", "Read 30 lessons.", "graduation-cap", "learning", "rare", 30, "lessons_read"),
        _badge("lessons-all", "Cover to Cover", "Read 80 lessons. That is nearly the whole course!", "landmark", "learning", "epic", 80, "lessons_read"),
        _badge("first-quiz", "Quiz Rookie", "Take your first module quiz.", "brain", "quizzes", "common", 1, "quizzes_taken"),
        _badge("quiz-80", "Sharp Mind", "Score 80% or more on a module quiz.", "target", "quizzes", "common", 1, "quizzes_80"),
        _badge("perfect-quiz", "Flawless", "Score 100% on a module quiz.", "gem", "quizzes", "rare", 1, "perfect_quizzes"),
        _badge("quiz-champion", "Quiz Champion", "Score 80% or more on the quizzes of 5 different modules.", "trophy", "quizzes", "rare", 5, "quizzes_80"),
        _badge("first-solve", "First Fix", "Solve your first coding problem.", "wrench", "coding", "common", 1, "problems_solved"),
        _badge("solve-10", "Problem Solver", "Solve 10 coding problems.", "puzzle", "coding", "common", 10, "problems_solved"),
        _badge("solve-30", "Code Warrior", "Solve 30 coding problems.", "swords", "coding", "rare", 30, "problems_solved"),
        _badge("solve-75", "Bug Crusher", "Solve 75 coding problems.", "bug", "coding", "epic", 75, "problems_solved"),
        _badge("first-try-5", "Sharpshooter", "Solve 5 problems on your very first submission.", "crosshair", "coding", "rare", 5, "first_try_solves"),
        _badge("hard-solve", "Tough Cookie", "Solve a hard problem.", "cookie", "coding", "rare", 1, "hard_solved"),
        _badge("hard-5", "Hard Mode", "Solve 5 hard problems.", "mountain", "coding", "epic", 5, "hard_solved"),
        _badge("streak-3", "On a Roll", "Learn 3 days in a row.", "flame", "streaks", "common", 3, "longest_streak"),
        _badge("streak-7", "Week Warrior", "Learn 7 days in a row.", "zap", "streaks", "rare", 7, "longest_streak"),
        _badge("streak-30", "Unstoppable", "Learn 30 days in a row.", "rocket", "streaks", "epic", 30, "longest_streak"),
        _badge("comeback", "Comeback Kid", "Come back and learn after a week away. Welcome back!", "sunrise", "streaks", "common", 1, "comebacks"),
        _badge("goal-getter", "Goal Getter", "Reach your daily goal on 7 different days.", "calendar-check", "streaks", "rare", 7, "daily_goals_met"),
    ]
    for number, (module_id, (name, icon)) in enumerate(zip(CORE_MODULE_IDS, _MODULE_BADGES), start=1):
        badges.append(
            BadgeDef(
                id=f"module-{number}",
                name=name,
                description=f"Master Module {number}: read every lesson, solve every problem and score {MODULE_QUIZ_PASS_PCT}% on the quiz.",
                icon=icon,
                category="modules",
                rarity="rare",
                target=1,
                current=_module_done(module_id),
            )
        )
    badges += [
        _badge("halfway-hero", "Halfway Hero", "Master 5 modules.", "medal", "modules", "epic", 5, "modules_completed"),
        _badge("python-graduate", "Python Graduate", "Master all 10 modules.", "crown", "modules", "legendary", 10, "modules_completed"),
        _badge("level-5", "High Five", "Reach level 5.", "hand", "levels", "common", 5, "level"),
        _badge("level-10", "Double Digits", "Reach level 10.", "award", "levels", "epic", 10, "level"),
        _badge("xp-1000", "XP Collector", "Earn 1,000 XP.", "sparkles", "levels", "rare", 1000, "xp_total"),
    ]
    return tuple(badges)


BADGES: Tuple[BadgeDef, ...] = _build_catalogue()
BADGES_BY_ID: Dict[str, BadgeDef] = {b.id: b for b in BADGES}
