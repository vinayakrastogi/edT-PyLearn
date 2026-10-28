"""
HTTP tests for the gamification hooks: lesson-view, quiz submit and problem submit award XP through
the real endpoints, the dashboard shows the live streak, and the /api/gamification endpoints work
end to end.

They run against the real content modules (grading really executes the shipped solutions) and an
in-memory SQLite database (see conftest.py). `app.dependency_overrides` supplies the database, the
logged-in user (a real User row) and, where a test needs full control, a tiny temporary content
directory. The clock is frozen, so streak and daily-goal assertions never depend on when the suite runs.
"""
import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.content_repository.file_repo import FileSystemContentRepository
from app.content_repository.loader import get_content_repo
from app.core.database import Base
from app.core.deps import get_current_user, get_db
from app.main import app
from app.models.gamification import GamificationProfile, UserBadge, XPEvent
from app.models.progress import CodeSubmission, LessonProgress, QuizAttempt, SubmissionStatus
from app.models.user import User
from app.services import gamification as g
from tests.conftest import make_user

REAL_CONTENT = Path(__file__).resolve().parents[2] / "content"
M1 = "module-1-introduction-to-python"
M2 = "module-2-operators-decision-making"
M4 = "module-4-strings-data-structures"
GENERATED = "generated-my-notes"
EASY = "02-celsius-to-fahrenheit"
EASY_2 = "01-rectangle-area"

# The frozen clock: noon UTC. With an X-TZ-Offset of 840 / 0 / -840 the learner's local date is
# the 9th / the 10th / the 11th.
NOW = datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc)

REWARD_KEYS = {
    "xp_gained", "events", "total_xp", "level", "previous_level", "level_title", "level_up",
    "xp_into_level", "xp_for_next_level", "streak", "new_badges", "daily",
}


# --------------------------------------------------------------------------------------
# Fixtures and helpers
# --------------------------------------------------------------------------------------


CLOCK = {"now": NOW}


def advance(days=1):
    """Let `days` whole days pass on the frozen clock."""
    CLOCK["now"] += timedelta(days=days)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    """Pin 'now' for every local-date calculation (the X-TZ-Offset header still shifts the local date)."""
    CLOCK["now"] = NOW
    real = g.local_today
    monkeypatch.setattr(g, "local_today", lambda tz_offset_minutes, now=None: real(tz_offset_minutes, now or CLOCK["now"]))


@pytest.fixture(autouse=True)
def _plain_xp_rules(no_farming_delays):
    """Most tests are about the XP rules, not the time guards (those have their own tests)."""


@pytest.fixture
def user(db):
    return make_user(db)


@pytest.fixture
def client(db):
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = lambda: db
    use_content(REAL_CONTENT)
    yield TestClient(app)
    app.dependency_overrides.clear()


def use_content(path):
    app.dependency_overrides[get_content_repo] = lambda: FileSystemContentRepository(str(path))


def login_as(who):
    app.dependency_overrides[get_current_user] = lambda: who


def tz(minutes):
    return {"X-TZ-Offset": str(minutes)}


def read_json(*parts):
    return json.loads(REAL_CONTENT.joinpath(*parts).read_text(encoding="utf-8"))


QUIZ_TOTAL = len(read_json(M1, "quiz.json")["questions"])  # every question of module 1's quiz


def doc_ids(client, module=M1):
    return [d["id"] for d in client.get(f"/api/modules/{module}").json()["docs"]]


def solution(module, problem_id):
    return read_json(module, "problems", f"{problem_id}.json")["solution_code"]


def quiz_answers(module, correct):
    """Answers that get exactly `correct` questions right (the first ones) and every other one wrong."""
    answers = {}
    for index, question in enumerate(read_json(module, "quiz.json")["questions"]):
        right = question["correct_answer"]
        if index < correct:
            answers[question["id"]] = right
        elif question["type"] == "true_false":
            answers[question["id"]] = not right
        else:
            answers[question["id"]] = (right + 1) % len(question["options"])
    return answers


def read_lesson(client, lesson_id, module=M1, **kwargs):
    r = client.post("/api/progress/lesson-view", json={"module_id": module, "lesson_id": lesson_id}, **kwargs)
    assert r.status_code == 200, r.text
    return r.json()


def submit_quiz(client, module, answers, **kwargs):
    r = client.post(f"/api/quiz/{module}/submit", json={"answers": answers}, **kwargs)
    assert r.status_code == 200, r.text
    return r.json()


def submit_code(client, module, problem_id, code, **kwargs):
    r = client.post(f"/api/problems/{module}/{problem_id}/submit", json={"code": code}, **kwargs)
    assert r.status_code == 200, r.text
    return r.json()


def set_goal(client, goal):
    r = client.patch("/api/gamification/settings", json={"daily_goal": goal})
    assert r.status_code == 200, r.text


def kinds(rewards):
    """{kind: amount} of the events in a rewards object."""
    return {e["kind"]: e["amount"] for e in rewards["events"]}


def badge_ids(rewards):
    return [b["id"] for b in rewards["new_badges"]]


def count(db, model, **filters):
    return db.query(model).filter_by(**filters).count()


def quiz_xp(correct, total):
    """round(50 * correct / total), halves rounded up, in exact integer arithmetic."""
    return (100 * correct + total) // (2 * total)


# A tiny but complete module: two lessons, one function problem and a two-question quiz.
TINY_LESSONS = ("01-intro", "02-next")
TINY_PROBLEM = "01-add"
TINY_SOLUTION = "def add(a, b):\n    return a + b\n"
TINY_WRONG = "def add(a, b):\n    return a - b\n"
TINY_RIGHT = {"q1": 1, "q2": True}  # both answers correct
TINY_HALF = {"q1": 1, "q2": False}  # one of two


def write_module(root: Path, module_id: str, *, generative: bool = False) -> None:
    folder = root / module_id
    (folder / "docs").mkdir(parents=True)
    (folder / "problems").mkdir()
    (folder / "module.yaml").write_text(
        f'id: {module_id}\ntitle: "Tiny module"\ndescription: "A fixture"\norder: 1\nicon: "terminal"\n'
        + ("is_generative: true\n" if generative else ""),
        encoding="utf-8",
    )
    for order, lesson_id in enumerate(TINY_LESSONS, start=1):
        (folder / "docs" / f"{lesson_id}.md").write_text(
            f'---\nid: {lesson_id}\ntitle: "Lesson {order}"\norder: {order}\nconcepts: ["basics"]\n---\n\n'
            f"# Lesson {order}\n\nHello.\n",
            encoding="utf-8",
        )
    problem = {
        "id": TINY_PROBLEM,
        "title": "Add",
        "type": "function",
        "difficulty": "easy",
        "description": "Add two numbers.",
        "starter_code": "def add(a, b):\n    pass\n",
        "concepts": ["operators"],
        "visible_tests": [{"input": [1, 2], "expected": "3"}],
        "hidden_tests": [{"input": [5, 7], "expected": "12"}],
        "hints": [],
        "solution_code": TINY_SOLUTION,
    }
    (folder / "problems" / f"{TINY_PROBLEM}.json").write_text(json.dumps(problem), encoding="utf-8")
    quiz = {
        "id": f"{module_id}-quiz",
        "title": "Quiz",
        "questions": [
            {"id": "q1", "type": "mcq", "question": "Pick yes.", "options": ["no", "yes"], "correct_answer": 1,
             "explanation": "Yes is right.", "concepts": ["basics"]},
            {"id": "q2", "type": "true_false", "question": "Python is fun.", "correct_answer": True,
             "explanation": "It is.", "concepts": ["logic"]},
        ],
    }
    (folder / "quiz.json").write_text(json.dumps(quiz), encoding="utf-8")


@pytest.fixture
def tiny(tmp_path, client):
    """Swap the content for two tiny modules: a core one (standing in for module 1) and a generated one."""
    write_module(tmp_path, M1)
    write_module(tmp_path, GENERATED, generative=True)
    use_content(tmp_path)
    return tmp_path


# --------------------------------------------------------------------------------------
# Lessons
# --------------------------------------------------------------------------------------


def test_lesson_view_twice_awards_xp_once(client, db, user):
    login_as(user)
    lesson = doc_ids(client)[0]

    body = read_lesson(client, lesson)
    assert body["lesson_id"] == lesson and body["is_complete"] is True and body["viewed_at"]
    first = body["rewards"]
    assert set(first) == REWARD_KEYS
    assert first["events"] == [{"kind": "lesson", "label": "Lesson read", "amount": 10}]
    assert (first["xp_gained"], first["total_xp"]) == (10, 10)
    assert (first["level"], first["previous_level"], first["level_up"], first["level_title"]) == (1, 1, False, "Hatchling")
    assert (first["xp_into_level"], first["xp_for_next_level"]) == (10, 100)
    assert first["streak"] == {
        "count": 1, "longest": 1, "freezes": 0, "extended": True, "used_freeze": False,
        "milestone": None, "broken_from": None, "active_today": True, "at_risk": False,
    }
    assert first["daily"] == {"goal": 30, "xp_today": 10, "goal_met": False, "just_met": False}
    assert badge_ids(first) == ["first-lesson"]

    again = read_lesson(client, lesson)
    assert again["viewed_at"] == body["viewed_at"]  # the stored row is returned, not a new one
    second = again["rewards"]
    assert second is not None  # a re-read still reports (streak) activity
    assert second["events"] == [] and second["xp_gained"] == 0 and second["total_xp"] == 10
    assert second["new_badges"] == []
    assert (second["streak"]["count"], second["streak"]["extended"], second["streak"]["active_today"]) == (1, False, True)

    assert count(db, LessonProgress, user_id=user.id) == 1
    assert count(db, XPEvent, user_id=user.id, kind="lesson") == 1
    assert client.get("/api/gamification/me").json()["xp_total"] == 10


def test_a_lesson_read_before_gamification_pays_when_it_is_opened_again(client, db, user):
    login_as(user)
    lesson = doc_ids(client)[0]
    db.add(LessonProgress(user_id=user.id, module_id=M1, lesson_id=lesson))  # saved long before the XP system existed
    db.commit()
    rewards = read_lesson(client, lesson)["rewards"]
    assert kinds(rewards) == {"lesson": 10} and rewards["streak"]["count"] == 1
    assert count(db, LessonProgress, user_id=user.id) == 1  # the old row is reused, not duplicated


def test_every_new_lesson_earns_ten_xp(client, user):
    login_as(user)
    lessons = doc_ids(client)[:3]
    totals = [read_lesson(client, lesson)["rewards"]["xp_gained"] for lesson in lessons[:2]]
    assert totals == [10, 10]
    assert client.get("/api/gamification/me").json()["xp_total"] == 20


def test_lesson_view_only_records_lessons_that_exist(client, db, user):
    login_as(user)
    lesson = doc_ids(client)[0]
    bad = [
        {"module_id": M1, "lesson_id": "no-such-lesson"},
        {"module_id": M2, "lesson_id": lesson},  # a real lesson id, but of another module
        {"module_id": "module-404", "lesson_id": lesson},
        {"module_id": "../etc", "lesson_id": lesson},
    ]
    codes = [client.post("/api/progress/lesson-view", json=payload).status_code for payload in bad]
    assert codes == [404, 404, 404, 400]
    # Made-up ids must neither fill the progress table nor earn XP or streak days.
    assert count(db, LessonProgress) == 0 and count(db, XPEvent) == 0 and count(db, GamificationProfile) == 0
    db.refresh(user)
    assert user.streak_count == 0


def test_the_daily_goal_bonus_pays_once_a_day_and_follows_the_chosen_goal(client, user):
    login_as(user)
    set_goal(client, 20)
    l1, l2, l3, l4 = doc_ids(client)[:4]

    first = read_lesson(client, l1)["rewards"]
    assert first["daily"] == {"goal": 20, "xp_today": 10, "goal_met": False, "just_met": False}

    second = read_lesson(client, l2)["rewards"]
    assert kinds(second) == {"lesson": 10, "daily_goal": 10}
    assert (second["xp_gained"], second["total_xp"]) == (20, 30)
    assert second["daily"] == {"goal": 20, "xp_today": 20, "goal_met": True, "just_met": True}  # the bonus is not counted

    third = read_lesson(client, l3)["rewards"]
    assert kinds(third) == {"lesson": 10}
    assert third["daily"] == {"goal": 20, "xp_today": 30, "goal_met": True, "just_met": False}

    me = client.get("/api/gamification/me").json()
    assert me["xp_total"] == 40 and me["daily"] == {"goal": 20, "xp_today": 30, "goal_met": True, "just_met": False}

    # The next local day starts from zero again.
    advance()
    tomorrow = read_lesson(client, l4)["rewards"]
    assert tomorrow["daily"] == {"goal": 20, "xp_today": 10, "goal_met": False, "just_met": False}


# --------------------------------------------------------------------------------------
# Quizzes
# --------------------------------------------------------------------------------------


def test_quiz_submit_awards_the_improvement_and_the_perfect_bonus(client, db, user):
    login_as(user)
    set_goal(client, 80)  # keep the daily-goal bonus out of the quiz arithmetic
    total = QUIZ_TOTAL
    low, high = total * 2 // 5, -(-total * 4 // 5)  # about 40%, and at least 80%
    paid_low, paid_high = quiz_xp(low, total), quiz_xp(high, total)
    assert 0 < paid_low < paid_high < 50

    body = submit_quiz(client, M1, quiz_answers(M1, low))
    assert set(body) == {"score", "max_score", "percentage", "per_question_results", "rewards"}
    assert body["score"] == low and body["max_score"] == total and len(body["per_question_results"]) == total
    first = body["rewards"]
    assert set(first) == REWARD_KEYS
    assert first["events"] == [{"kind": "quiz", "label": "Quiz score", "amount": paid_low}]
    assert first["xp_gained"] == first["total_xp"] == paid_low
    assert badge_ids(first) == ["first-quiz"]
    assert first["streak"]["count"] == 1 and first["streak"]["extended"] is True

    # The same score again earns nothing: only an improvement is paid.
    same = submit_quiz(client, M1, quiz_answers(M1, low))["rewards"]
    assert same["events"] == [] and same["xp_gained"] == 0 and same["total_xp"] == paid_low

    better = submit_quiz(client, M1, quiz_answers(M1, high))["rewards"]
    assert kinds(better) == {"quiz": paid_high - paid_low}  # the delta, not the whole score again
    assert badge_ids(better) == ["quiz-80"]

    worse = submit_quiz(client, M1, quiz_answers(M1, low // 2))["rewards"]
    assert worse["events"] == [] and worse["xp_gained"] == 0

    perfect = submit_quiz(client, M1, quiz_answers(M1, total))["rewards"]
    assert kinds(perfect) == {"quiz": 50 - paid_high, "quiz_perfect": 25}
    assert badge_ids(perfect) == ["perfect-quiz"]
    assert perfect["total_xp"] == 75

    repeat = submit_quiz(client, M1, quiz_answers(M1, total))["rewards"]
    assert repeat["events"] == [] and repeat["total_xp"] == 75

    # In total a module's quiz is worth 50 XP, plus the perfect bonus, however many attempts it took.
    assert count(db, QuizAttempt, user_id=user.id) == 6
    quiz_paid = sum(e.amount for e in db.query(XPEvent).filter_by(user_id=user.id, kind="quiz"))
    assert quiz_paid == 50 and count(db, XPEvent, user_id=user.id, kind="quiz_perfect") == 1
    assert client.get("/api/gamification/me").json()["xp_total"] == 75


def test_a_quiz_with_every_answer_wrong_earns_nothing_but_counts_as_activity(client, user):
    login_as(user)
    rewards = submit_quiz(client, M1, quiz_answers(M1, 0))["rewards"]
    assert rewards["events"] == [] and rewards["xp_gained"] == 0
    assert rewards["streak"]["count"] == 1 and rewards["streak"]["extended"] is True
    assert badge_ids(rewards) == ["first-quiz"]  # taking the quiz is what that badge asks for


# --------------------------------------------------------------------------------------
# Coding problems
# --------------------------------------------------------------------------------------

def test_a_problem_solved_on_the_first_try_pays_once(client, db, user):
    login_as(user)
    set_goal(client, 80)
    body = submit_code(client, M1, EASY, solution(M1, EASY))
    assert body["status"] == "PASS" and body["passed_count"] == body["total_count"]
    first = body["rewards"]
    assert set(first) == REWARD_KEYS
    assert kinds(first) == {"problem": 20, "problem_first_try": 10}
    assert first["xp_gained"] == first["total_xp"] == 30
    assert badge_ids(first) == ["first-solve"]
    assert first["streak"]["count"] == 1 and first["streak"]["extended"] is True

    again = submit_code(client, M1, EASY, solution(M1, EASY))
    assert again["status"] == "PASS"  # grading is unaffected
    assert again["rewards"]["events"] == [] and again["rewards"]["xp_gained"] == 0
    assert again["rewards"]["total_xp"] == 30 and again["rewards"]["new_badges"] == []

    assert count(db, CodeSubmission, user_id=user.id) == 2  # every graded submission is kept
    assert count(db, XPEvent, user_id=user.id, kind="problem") == 1
    assert count(db, XPEvent, user_id=user.id, kind="problem_first_try") == 1

    # Every problem has its own first try, and other learners' earlier attempts do not count.
    other = make_user(db, name="Someone Else")
    db.add(CodeSubmission(user_id=other.id, module_id=M1, problem_id=EASY_2, code="x", status=SubmissionStatus.FAIL))
    db.commit()
    second = submit_code(client, M1, EASY_2, solution(M1, EASY_2))
    assert kinds(second["rewards"]) == {"problem": 20, "problem_first_try": 10}


def test_a_pass_after_a_failed_try_has_no_first_try_bonus(client, db, user):
    login_as(user)
    set_goal(client, 80)
    wrong = submit_code(client, M1, EASY_2, "def area(width, height):\n    return width + height\n")
    assert wrong["status"] == "FAIL"
    assert wrong["rewards"]["events"] == [] and wrong["rewards"]["xp_gained"] == 0

    passed = submit_code(client, M1, EASY_2, solution(M1, EASY_2))
    assert passed["status"] == "PASS"
    assert kinds(passed["rewards"]) == {"problem": 20}  # no problem_first_try

    again = submit_code(client, M1, EASY_2, solution(M1, EASY_2))
    assert again["rewards"]["events"] == [] and again["rewards"]["total_xp"] == 20
    assert count(db, XPEvent, user_id=user.id, kind="problem_first_try") == 0


def test_failed_and_broken_submissions_earn_nothing_but_still_count_as_activity(client, db, user):
    login_as(user)
    broken = submit_code(client, M1, EASY, "def celsius_to_fahrenheit(:\n")
    assert broken["status"] == "ERROR"
    assert broken["rewards"]["xp_gained"] == 0 and broken["rewards"]["events"] == []
    assert broken["rewards"]["streak"]["count"] == 1 and broken["rewards"]["streak"]["extended"] is True

    wrong = submit_code(client, M1, EASY, "def celsius_to_fahrenheit(c):\n    return 0\n")
    assert wrong["status"] == "FAIL" and wrong["rewards"]["xp_gained"] == 0
    assert wrong["rewards"]["streak"]["count"] == 1 and wrong["rewards"]["streak"]["extended"] is False

    assert count(db, CodeSubmission, user_id=user.id) == 2
    assert count(db, XPEvent, user_id=user.id) == 0
    assert client.get("/api/gamification/me").json()["streak"]["count"] == 1


def test_earlier_submissions_from_before_gamification_count_as_earlier_tries(client, db, user):
    login_as(user)
    set_goal(client, 80)
    # A failed try saved long before the XP system existed (no ledger rows, no profile).
    db.add(CodeSubmission(
        user_id=user.id, module_id=M1, problem_id=EASY, code="x", status=SubmissionStatus.FAIL,
    ))
    db.commit()
    passed = submit_code(client, M1, EASY, solution(M1, EASY))
    assert kinds(passed["rewards"]) == {"problem": 20}  # not the learner's very first submission


def test_submissions_to_unknown_problems_are_not_recorded(client, db, user):
    login_as(user)
    r = client.post(f"/api/problems/{M1}/no-such-problem/submit", json={"code": "print(1)"})
    assert r.status_code == 404
    assert count(db, CodeSubmission) == 0 and count(db, XPEvent) == 0 and count(db, GamificationProfile) == 0


@pytest.mark.parametrize(
    "module, problem_id, difficulty, xp",
    [(M1, EASY, "easy", 20), (M1, "10-bill-splitter", "medium", 35), (M4, "11-phone-book-program", "hard", 60)],
)
def test_problem_xp_follows_the_difficulty_in_the_content(client, user, module, problem_id, difficulty, xp):
    assert read_json(module, "problems", f"{problem_id}.json")["difficulty"] == difficulty  # guards the fixture choice
    login_as(user)
    set_goal(client, 80)
    rewards = submit_code(client, module, problem_id, solution(module, problem_id))["rewards"]
    assert kinds(rewards) == {"problem": xp, "problem_first_try": 10}
    assert rewards["xp_gained"] == xp + 10
    # A hard problem also unlocks the Tough Cookie badge (the difficulty is remembered in the ledger).
    assert ("hard-solve" in badge_ids(rewards)) == (difficulty == "hard")


# --------------------------------------------------------------------------------------
# Generated modules and module mastery (tiny content, so every step is fast)
# --------------------------------------------------------------------------------------


def test_generated_modules_earn_no_xp_but_still_count_for_the_streak(client, db, user, tiny):
    login_as(user)
    lesson = read_lesson(client, "01-intro", GENERATED)["rewards"]
    quiz = submit_quiz(client, GENERATED, TINY_RIGHT)["rewards"]
    problem = submit_code(client, GENERATED, TINY_PROBLEM, TINY_SOLUTION)
    assert problem["status"] == "PASS"
    for rewards in (lesson, quiz, problem["rewards"]):
        assert rewards["xp_gained"] == 0 and rewards["events"] == [] and rewards["new_badges"] == []
        assert rewards["total_xp"] == 0 and rewards["streak"]["count"] == 1
    assert lesson["streak"]["extended"] is True and quiz["streak"]["extended"] is False

    assert count(db, XPEvent) == 0 and count(db, UserBadge) == 0
    me = client.get("/api/gamification/me").json()
    assert me["xp_total"] == 0 and me["recent_events"] == [] and me["streak"]["count"] == 1
    # The learner's own progress is saved as usual.
    assert count(db, LessonProgress, module_id=GENERATED) == 1
    assert count(db, QuizAttempt, module_id=GENERATED) == 1
    assert count(db, CodeSubmission, module_id=GENERATED, status=SubmissionStatus.PASS) == 1

    # Core activity the next local day carries the streak on and earns XP as usual.
    advance()
    next_day = read_lesson(client, "01-intro", M1)["rewards"]
    assert next_day["xp_gained"] == 10 and next_day["streak"]["count"] == 2


def test_the_first_try_bonus_is_counted_per_module(client, user, tiny):
    login_as(user)
    set_goal(client, 80)
    submit_code(client, GENERATED, TINY_PROBLEM, TINY_WRONG)  # the same problem id, but in another module
    passed = submit_code(client, M1, TINY_PROBLEM, TINY_SOLUTION)
    assert kinds(passed["rewards"]) == {"problem": 20, "problem_first_try": 10}


@pytest.mark.parametrize("last", ["lesson", "problem", "quiz"])
def test_module_mastery_is_paid_by_whichever_request_finishes_the_module(client, db, user, tiny, last):
    login_as(user)
    steps = {
        "lesson": lambda: read_lesson(client, "02-next"),
        "problem": lambda: submit_code(client, M1, TINY_PROBLEM, TINY_SOLUTION),
        "quiz": lambda: submit_quiz(client, M1, TINY_RIGHT),
    }
    read_lesson(client, "01-intro")  # the first of the two lessons
    order = [name for name in steps if name != last] + [last]
    responses = [steps[name]()["rewards"] for name in order]

    # Only the final request completes the module: 150 XP and the Pythonista badge.
    assert [("module_complete" in kinds(r)) for r in responses] == [False, False, True]
    final = responses[-1]
    assert kinds(final)["module_complete"] == 150 and "module-1" in badge_ids(final)

    # Everything together: 2 lessons + a solved problem (+ first try) + a perfect quiz + the module
    # + the daily goal bonus. One of the responses crossed 100 XP and levelled up.
    assert final["total_xp"] == 2 * 10 + (20 + 10) + (50 + 25) + 150 + 10 == 285
    assert final["level"] == 2 and final["level_title"] == "Sprout"
    ups = [r for r in responses if r["level_up"]]
    assert len(ups) == 1 and (ups[0]["previous_level"], ups[0]["level"]) == (1, 2)

    # Repeating the last step cannot pay the module again.
    again = steps[last]()["rewards"]
    assert again["xp_gained"] == 0 and again["total_xp"] == 285
    assert count(db, XPEvent, user_id=user.id, kind="module_complete") == 1
    assert client.get("/api/gamification/me").json()["xp_total"] == 285


def test_a_real_module_can_be_mastered_end_to_end(client, db, user):
    """Every lesson, every problem (with its shipped solution) and a perfect quiz: the real content lines up."""
    login_as(user)
    lessons = doc_ids(client)
    problems = sorted(p.stem for p in (REAL_CONTENT / M1 / "problems").glob("*.json"))
    xp_by_difficulty = {"easy": 20, "medium": 35, "hard": 60}

    for lesson in lessons:
        assert "module_complete" not in kinds(read_lesson(client, lesson)["rewards"])
    for problem_id in problems:
        body = submit_code(client, M1, problem_id, solution(M1, problem_id))
        assert body["status"] == "PASS", problem_id
        assert "module_complete" not in kinds(body["rewards"])
    final = submit_quiz(client, M1, quiz_answers(M1, QUIZ_TOTAL))["rewards"]

    assert kinds(final)["module_complete"] == 150 and "module-1" in badge_ids(final)
    expected = (
        10 * len(lessons)
        + sum(xp_by_difficulty[read_json(M1, "problems", f"{p}.json")["difficulty"]] + 10 for p in problems)
        + 50 + 25  # the quiz and its perfect bonus
        + 150  # the module
        + 10  # the daily goal, once
    )
    assert final["total_xp"] == expected == client.get("/api/gamification/me").json()["xp_total"]
    earned = {b["id"] for b in client.get("/api/gamification/badges").json()["badges"] if b["earned"]}
    assert {"first-lesson", "first-quiz", "quiz-80", "perfect-quiz", "first-solve", "solve-10", "first-try-5", "module-1"} <= earned
    assert count(db, XPEvent, user_id=user.id, kind="module_complete") == 1


def test_a_weak_quiz_blocks_mastery_until_a_retake(client, user, tiny):
    login_as(user)
    for lesson in TINY_LESSONS:
        read_lesson(client, lesson)
    submit_code(client, M1, TINY_PROBLEM, TINY_SOLUTION)

    weak = submit_quiz(client, M1, {"q1": 0, "q2": False})["rewards"]  # 0%: below the 70% pass mark
    assert "module_complete" not in kinds(weak)
    half = submit_quiz(client, M1, TINY_HALF)["rewards"]  # 50%: still below
    assert "module_complete" not in kinds(half) and kinds(half)["quiz"] == 25

    retake = submit_quiz(client, M1, TINY_RIGHT)["rewards"]
    assert kinds(retake) == {"quiz": 25, "quiz_perfect": 25, "module_complete": 150}
    assert "module-1" in badge_ids(retake)


# --------------------------------------------------------------------------------------
# Abuse resistance
# --------------------------------------------------------------------------------------


class CaseInsensitiveRepo(FileSystemContentRepository):
    """What a case-insensitive filesystem (macOS, Windows) does: any spelling of a module id resolves."""

    def _module_path(self, module_id):
        return super()._module_path(module_id.lower())


def test_another_spelling_of_an_id_is_rejected_before_anything_is_saved(client, db, user):
    app.dependency_overrides[get_content_repo] = lambda: CaseInsensitiveRepo(str(REAL_CONTENT))
    login_as(user)
    lesson = doc_ids(client)[0]
    shouting = M1.upper()
    answers = quiz_answers(M1, QUIZ_TOTAL)

    assert client.post("/api/progress/lesson-view", json={"module_id": shouting, "lesson_id": lesson}).status_code == 404
    assert client.post(f"/api/quiz/{shouting}/submit", json={"answers": answers}).status_code == 404
    assert client.post(f"/api/problems/{shouting}/{EASY}/submit", json={"code": solution(M1, EASY)}).status_code == 404
    # The module is spelled right but the problem is not: just as unknown.
    for spelling in (EASY.upper(), EASY.title()):
        assert client.post(f"/api/problems/{M1}/{spelling}/submit", json={"code": solution(M1, EASY)}).status_code == 404
    assert count(db, XPEvent) == 0 and count(db, GamificationProfile) == 0 and count(db, LessonProgress) == 0
    assert count(db, QuizAttempt) == 0 and count(db, CodeSubmission) == 0

    assert read_lesson(client, lesson)["rewards"]["xp_gained"] == 10  # the real spelling still works


def test_spellings_cannot_stack_up_badge_statistics_even_when_rows_already_exist(db, user):
    """Rows saved under other spellings (before ids were validated) count as the one module they are."""
    for spelling in (M1, M1.upper(), M1.title(), "MODULE-1-introduction-to-python", "module-1-introduction-to-PYTHON"):
        db.add(QuizAttempt(user_id=user.id, module_id=spelling, quiz_id="q", answers={}, score=10, max_score=10, per_question_results=[]))
        for problem in ("02-celsius-to-fahrenheit", "02-CELSIUS-TO-FAHRENHEIT"):
            db.add(CodeSubmission(user_id=user.id, module_id=spelling, problem_id=problem, code="x", status=SubmissionStatus.PASS))
    db.add(QuizAttempt(user_id=user.id, module_id="GENERATED-MY-NOTES", quiz_id="q", answers={}, score=10, max_score=10, per_question_results=[]))
    db.commit()
    stats = g._collect_stats(db, user.id, xp_total=0, longest_streak=0)
    assert stats["quizzes_taken"] == 1 and stats["quizzes_80"] == 1  # one module; the generated one counts for nothing
    assert stats["problems_solved"] == 2  # two problems, however often and however they are spelled
    champion = next(b for b in g.list_badges(db, user) if b.id == "quiz-champion")
    assert (champion.earned, champion.progress.current) == (False, 1)


# --------------------------------------------------------------------------------------
# A gamification failure never breaks learning
# --------------------------------------------------------------------------------------


def _boom(*args, **kwargs):
    raise RuntimeError("gamification is down")


@pytest.mark.parametrize("hook", ["record_lesson_read", "record_quiz_attempt", "record_problem_submission"])
def test_a_gamification_failure_never_breaks_the_learning_flow(client, db, user, monkeypatch, caplog, hook):
    login_as(user)
    lesson = doc_ids(client)[0]
    monkeypatch.setattr(g, hook, _boom)
    with caplog.at_level(logging.ERROR):
        if hook == "record_lesson_read":
            body = read_lesson(client, lesson)
            assert body["lesson_id"] == lesson and body["is_complete"] is True
            assert count(db, LessonProgress, user_id=user.id, lesson_id=lesson) == 1
        elif hook == "record_quiz_attempt":
            body = submit_quiz(client, M1, quiz_answers(M1, 10))
            assert body["score"] == 10 and body["max_score"] == QUIZ_TOTAL
            assert count(db, QuizAttempt, user_id=user.id, score=10.0) == 1
        else:
            body = submit_code(client, M1, EASY, solution(M1, EASY))
            assert body["status"] == "PASS"
            assert count(db, CodeSubmission, user_id=user.id, status=SubmissionStatus.PASS) == 1
    assert body["rewards"] is None
    assert any("Gamification failed" in record.getMessage() for record in caplog.records)
    assert count(db, XPEvent) == 0


def test_learning_still_works_before_the_gamification_migration_is_applied(client, db, user):
    """The most likely real-world failure: the new tables do not exist yet. Learners must not notice."""
    Base.metadata.drop_all(
        db.get_bind(), tables=[UserBadge.__table__, XPEvent.__table__, GamificationProfile.__table__]
    )
    login_as(user)
    lesson = doc_ids(client)[0]

    assert read_lesson(client, lesson)["rewards"] is None
    quiz = submit_quiz(client, M1, quiz_answers(M1, 5))
    assert quiz["score"] == 5 and quiz["rewards"] is None
    code = submit_code(client, M1, EASY, solution(M1, EASY))
    assert code["status"] == "PASS" and code["rewards"] is None
    assert read_lesson(client, lesson)["rewards"] is None  # and the session is still healthy afterwards

    board = dashboard(client)
    assert board["streak_count"] == 0
    by_id = {m["module_id"]: m for m in board["modules"]}
    assert (by_id[M1]["docs_read"], by_id[M1]["quiz_attempts"], by_id[M1]["problems_solved"]) == (1, 1, 1)
    assert client.post("/api/progress/track-access", json={"path": "/x", "title": "X"}).status_code == 200
    assert count(db, LessonProgress) == 1 and count(db, QuizAttempt) == 1 and count(db, CodeSubmission) == 1


def test_a_failure_after_the_awards_rolls_everything_back_and_the_next_request_recovers(client, db, user, monkeypatch):
    login_as(user)
    lesson = doc_ids(client)[0]
    real = g.level_progress
    calls = []

    def fails_once(xp):  # the very last step of a reward, after the XP was written but before the commit
        calls.append(xp)
        if len(calls) == 1:
            raise RuntimeError("boom")
        return real(xp)

    monkeypatch.setattr(g, "level_progress", fails_once)
    body = read_lesson(client, lesson)
    assert body["rewards"] is None
    assert count(db, LessonProgress, user_id=user.id) == 1  # the lesson itself was saved

    # Nothing was half-saved: no XP, no streak day, no badge, not even a profile row.
    db.expire_all()
    assert count(db, XPEvent) == 0 and count(db, UserBadge) == 0 and count(db, GamificationProfile) == 0
    assert user.streak_count == 0

    # Viewing the lesson again now pays out exactly as if nothing had happened.
    retry = read_lesson(client, lesson)["rewards"]
    assert retry["xp_gained"] == 10 and retry["streak"]["count"] == 1 and badge_ids(retry) == ["first-lesson"]
    assert client.get("/api/gamification/me").json()["xp_total"] == 10


# --------------------------------------------------------------------------------------
# The learner's local date (X-TZ-Offset)
# --------------------------------------------------------------------------------------


def change_timezone(db, user, hours=7):
    """The learner really moved: their previous offset change is `hours` old (older than the cooldown)."""
    profile = db.get(GamificationProfile, user.id)
    profile.tz_changed_at = datetime.now(timezone.utc) - timedelta(hours=hours)
    db.commit()


def test_the_tz_offset_header_decides_which_local_day_an_activity_counts_for(client, db, user):
    login_as(user)
    l1, l2, l3, l4 = doc_ids(client)[:4]

    day1 = read_lesson(client, l1, headers=tz(840))["rewards"]  # UTC-14: still the 9th
    assert (day1["streak"]["count"], day1["streak"]["extended"]) == (1, True)
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="lesson").one().local_date == date(2026, 3, 9)

    # The same learner with another offset straight away: the header is not believed yet (still the 9th).
    assert read_lesson(client, l2, headers=tz(0))["rewards"]["streak"]["extended"] is False

    # A learner who really changed time zone (long enough ago) is believed: UTC is already the 10th.
    change_timezone(db, user)
    day2 = read_lesson(client, l3, headers=tz(0))["rewards"]
    assert (day2["streak"]["count"], day2["streak"]["extended"]) == (2, True)

    same_day = read_lesson(client, l4, headers=tz(0))["rewards"]  # the 10th again: nothing moves
    assert (same_day["streak"]["count"], same_day["streak"]["extended"], same_day["streak"]["milestone"]) == (2, False, None)

    me = client.get("/api/gamification/me", headers=tz(0)).json()
    assert me["streak"]["count"] == 2 and me["streak"]["longest"] == 2
    # The XP of each activity is filed under the local day it happened on.
    assert {p["date"]: p["xp"] for p in me["weekly"][-2:]} == {"2026-03-09": 20, "2026-03-10": 20}


def test_a_forged_tz_offset_cannot_mint_streak_days_or_daily_goal_bonuses(client, db, user):
    """840 / 0 / -840 in a row used to be three different local dates at one real instant."""
    login_as(user)
    lessons = doc_ids(client)[:9]
    streaks, goals = [], 0
    for offset, group in ((840, lessons[0:3]), (0, lessons[3:6]), (-840, lessons[6:9])):
        for lesson in group:
            rewards = read_lesson(client, lesson, headers=tz(offset))["rewards"]
            goals += "daily_goal" in kinds(rewards)
        streaks.append((rewards["streak"]["count"], rewards["streak"]["milestone"]))
    assert streaks == [(1, None)] * 3  # one day, whatever the header says
    assert goals == 1  # and a single daily-goal bonus
    assert count(db, XPEvent, user_id=user.id, kind="streak_milestone") == 0
    assert {e.local_date for e in db.query(XPEvent).filter_by(user_id=user.id)} == {date(2026, 3, 9)}
    assert db.get(GamificationProfile, user.id).tz_offset == 840


def test_a_forged_tz_offset_cannot_backfill_a_missed_day_without_a_freeze(client, db, user):
    login_as(user)
    lessons = doc_ids(client)
    read_lesson(client, lessons[0])  # the 10th
    advance(2)  # the 12th: the 11th was missed, no freeze banked
    for offset, lesson in ((840, lessons[1]), (0, lessons[2])):  # 840 would make it the 11th
        read_lesson(client, lesson, headers=tz(offset))
    # The learner's offset is 0 and stays 0: the streak broke honestly (count restarted at 1).
    me = client.get("/api/gamification/me").json()
    assert me["streak"]["count"] == 1 and me["streak"]["freezes"] == 0


def test_the_local_date_never_goes_backwards(client, db, user):
    login_as(user)
    lessons = doc_ids(client)
    read_lesson(client, lessons[0], headers=tz(-840))  # the 11th
    change_timezone(db, user)
    flown_west = read_lesson(client, lessons[1], headers=tz(840))["rewards"]  # would be the 9th
    assert flown_west["streak"]["extended"] is False and flown_west["streak"]["count"] == 1
    assert flown_west["daily"]["xp_today"] == 20  # today's XP is not wiped by the earlier date
    assert {e.local_date for e in db.query(XPEvent).filter_by(user_id=user.id)} == {date(2026, 3, 11)}
    me = client.get("/api/gamification/me", headers=tz(840)).json()
    assert me["daily"]["xp_today"] == 20 and me["weekly"][-1]["date"] == "2026-03-11"


@pytest.mark.parametrize("opening", ["quiz", "problem"])
def test_quiz_and_problem_submissions_use_the_tz_offset_too(client, user, opening):
    login_as(user)
    if opening == "quiz":
        first = submit_quiz(client, M1, quiz_answers(M1, QUIZ_TOTAL), headers=tz(840))["rewards"]  # the 9th
    else:
        first = submit_code(client, M1, EASY, solution(M1, EASY), headers=tz(840))["rewards"]  # the 9th
    assert first["streak"]["count"] == 1
    # A day later (still UTC-14) it is the 10th: the second day in a row, which is only true if the
    # first activity was filed under the 9th.
    advance()
    next_day = read_lesson(client, doc_ids(client)[0], headers=tz(840))["rewards"]
    assert (next_day["streak"]["count"], next_day["streak"]["extended"]) == (2, True)


@pytest.mark.parametrize(
    "header, local_date",
    [("not-a-number", "2026-03-10"), ("", "2026-03-10"), ("99999", "2026-03-09"), ("-99999", "2026-03-11")],
)
def test_an_invalid_or_out_of_range_tz_offset_is_treated_as_utc_or_clamped(client, db, user, header, local_date):
    login_as(user)
    read_lesson(client, doc_ids(client)[0], headers={"X-TZ-Offset": header})
    assert db.query(XPEvent).filter_by(user_id=user.id, kind="lesson").one().local_date.isoformat() == local_date


# --------------------------------------------------------------------------------------
# Dashboard, module progress and track-access
# --------------------------------------------------------------------------------------


def dashboard(client, **kwargs):
    r = client.get("/api/progress/dashboard", **kwargs)
    assert r.status_code == 200, r.text
    return r.json()


def test_the_dashboard_streak_follows_the_learners_local_day(client, db, user, tiny):
    login_as(user)
    assert dashboard(client)["streak_count"] == 0  # a brand new learner

    read_lesson(client, "01-intro", headers=tz(840))  # the 9th
    assert dashboard(client, headers=tz(840))["streak_count"] == 1  # active today
    advance()
    assert dashboard(client, headers=tz(840))["streak_count"] == 1  # active yesterday: at risk, still alive
    advance()
    assert dashboard(client, headers=tz(840))["streak_count"] == 0  # two days ago and no freeze: lapsed
    db.refresh(user)
    assert user.streak_count == 1  # the stored counter is only corrected by the next activity...
    # ...but the dashboard and the XP chip never disagree about it.
    assert client.get("/api/gamification/me", headers=tz(840)).json()["streak"]["count"] == 0


def test_the_dashboard_keeps_a_streak_alive_that_a_banked_freeze_will_cover(client, db, tiny):
    seven = make_user(db, name="Seven Days")
    six = make_user(db, name="Six Days")
    # Both were last active on the 8th, two days before "today"; only a 7-day streak banks a freeze.
    for who, first_day in ((seven, 2), (six, 3)):
        for day in range(first_day, 9):
            g.record_lesson_read(db, who, M1, f"day-{day}", today=date(2026, 3, day))

    login_as(seven)
    assert dashboard(client)["streak_count"] == 7
    streak = client.get("/api/gamification/me").json()["streak"]
    assert (streak["count"], streak["freezes"], streak["active_today"], streak["at_risk"]) == (7, 1, False, False)

    login_as(six)
    assert dashboard(client)["streak_count"] == 0


def test_the_dashboard_still_loads_when_gamification_fails(client, user, tiny, monkeypatch, caplog):
    login_as(user)
    read_lesson(client, "01-intro")
    monkeypatch.setattr(g, "get_summary", _boom)
    with caplog.at_level(logging.ERROR):
        body = dashboard(client)
    assert body["streak_count"] == 0  # never shows a streak it cannot vouch for
    assert len(body["modules"]) == 2 and any("Gamification failed" in r.getMessage() for r in caplog.records)


def test_track_access_remembers_the_page_but_no_longer_touches_the_streak(client, db, user):
    login_as(user)
    r = client.post("/api/progress/track-access", json={"path": "/modules/x/docs/y", "title": "A lesson"})
    assert r.status_code == 200 and r.json() == {"status": "ok"}
    db.refresh(user)
    assert (user.last_accessed_path, user.last_accessed_title) == ("/modules/x/docs/y", "A lesson")
    assert user.streak_count == 0 and user.last_streak_update is None
    assert count(db, GamificationProfile) == 0  # page views create no gamification state either

    read_lesson(client, doc_ids(client)[0])
    db.refresh(user)
    stamp = user.last_streak_update
    assert user.streak_count == 1 and stamp is not None
    for path in ("/a", "/b"):
        assert client.post("/api/progress/track-access", json={"path": path, "title": "t"}).status_code == 200
    db.refresh(user)
    assert user.streak_count == 1 and user.last_streak_update == stamp and user.last_accessed_path == "/b"


def test_dashboard_and_module_progress_report_the_same_numbers(client, db, user, tiny):
    login_as(user)
    read_lesson(client, "01-intro")
    submit_quiz(client, M1, TINY_HALF)
    submit_code(client, M1, TINY_PROBLEM, TINY_WRONG)  # a failed try does not count as solved
    submit_code(client, M1, TINY_PROBLEM, TINY_SOLUTION)
    submit_code(client, M1, TINY_PROBLEM, TINY_SOLUTION)  # solving it twice still counts once
    read_lesson(client, "01-intro", GENERATED)

    single = client.get(f"/api/progress/{M1}")
    assert single.status_code == 200
    assert single.json() == {
        "module_id": M1, "total_docs": 2, "docs_read": 1, "quiz_attempts": 1, "best_quiz_score": 50.0,
        "total_problems": 1, "problems_solved": 1, "completion_percentage": 50.0,
        "viewed_docs": ["01-intro"], "passed_problems": [TINY_PROBLEM],
    }

    body = dashboard(client)
    by_id = {m["module_id"]: m for m in body["modules"]}
    assert set(by_id) == {M1, GENERATED}
    assert by_id[M1] == single.json()
    assert by_id[GENERATED]["docs_read"] == 1 and by_id[GENERATED]["completion_percentage"] == 25.0
    assert client.get(f"/api/progress/{GENERATED}").json() == by_id[GENERATED]

    # Concept mastery combines quiz answers and problem attempts (1 right quiz answer, 1 wrong one, 2 passes of 3 tries).
    mastery = {m["concept"]: (m["correct"], m["total"], m["percentage"]) for m in body["mastery_stats"]}
    assert mastery == {"basics": (1, 1, 100.0), "logic": (0, 1, 0.0), "operators": (2, 3, 66.7)}
    assert [m["concept"] for m in body["mastery_stats"]][-1] == "logic"  # sorted best first

    # A perfect quiz is what lifts the module's completion to the next level.
    submit_quiz(client, M1, TINY_RIGHT)
    assert client.get(f"/api/progress/{M1}").json()["completion_percentage"] == 75.0
    assert client.get(f"/api/progress/{M1}").json()["best_quiz_score"] == 100.0

    # A lesson that is not marked complete is not "read" - for both endpoints alike.
    db.add(LessonProgress(user_id=user.id, module_id=M1, lesson_id="02-next", is_complete=False))
    db.commit()
    assert client.get(f"/api/progress/{M1}").json()["docs_read"] == 1
    assert {m["module_id"]: m for m in dashboard(client)["modules"]}[M1]["docs_read"] == 1


def test_module_progress_for_an_unknown_module_is_a_404(client, user):
    login_as(user)
    assert client.get("/api/progress/module-404").status_code == 404


# --------------------------------------------------------------------------------------
# The /api/gamification endpoints, end to end
# --------------------------------------------------------------------------------------


def test_summary_reflects_what_the_learner_did(client, user):
    login_as(user)
    fresh = client.get("/api/gamification/me").json()
    assert fresh["xp_total"] == 0 and fresh["level"] == 1 and fresh["badges_earned"] == 0
    assert fresh["streak"]["count"] == 0 and fresh["streak"]["active_today"] is False
    assert fresh["recent_events"] == [] and fresh["recent_badges"] == [] and len(fresh["weekly"]) == 7

    l1, l2 = doc_ids(client)[:2]
    read_lesson(client, l1)
    read_lesson(client, l2)
    me = client.get("/api/gamification/me").json()
    assert me["xp_total"] == 20 and (me["level"], me["level_title"]) == (1, "Hatchling")
    assert (me["xp_into_level"], me["xp_for_next_level"], me["next_level_xp"]) == (20, 100, 100)
    assert me["streak"]["count"] == 1 and me["streak"]["active_today"] is True and me["streak"]["at_risk"] is False
    assert me["daily"] == {"goal": 30, "xp_today": 20, "goal_met": False, "just_met": False}
    assert me["weekly"][-1] == {"date": "2026-03-10", "xp": 20} and [p["xp"] for p in me["weekly"][:-1]] == [0] * 6
    assert (me["badges_earned"], me["badges_total"]) == (1, 35)
    assert [b["id"] for b in me["recent_badges"]] == ["first-lesson"]
    assert [(e["kind"], e["label"], e["amount"]) for e in me["recent_events"]] == [("lesson", "Lesson read", 10)] * 2
    assert me["show_on_leaderboard"] is False


def test_badges_catalogue_shows_progress_and_what_was_earned(client, user):
    login_as(user)
    before = client.get("/api/gamification/badges").json()["badges"]
    assert len(before) == 35 and len({b["id"] for b in before}) == 35
    assert before[0]["id"] == "first-lesson" and before[-1]["id"] == "xp-1000"
    assert all(b["earned"] is False and b["earned_at"] is None for b in before)
    assert all(0 <= b["progress"]["current"] <= b["progress"]["target"] for b in before)
    by_id = {b["id"]: b for b in before}
    assert by_id["first-lesson"]["progress"] == {"current": 0, "target": 1}
    assert by_id["level-5"]["progress"] == {"current": 1, "target": 5}  # everyone starts on level 1

    read_lesson(client, doc_ids(client)[0])
    after = {b["id"]: b for b in client.get("/api/gamification/badges").json()["badges"]}
    first = after["first-lesson"]
    assert first["earned"] is True and first["earned_at"] and first["progress"] == {"current": 1, "target": 1}
    assert (first["name"], first["icon"], first["category"], first["rarity"]) == ("First Steps", "book-open", "learning", "common")
    assert after["lessons-10"]["earned"] is False and after["lessons-10"]["progress"] == {"current": 1, "target": 10}


def test_settings_are_validated_saved_and_not_counted_as_activity(client, db, user):
    login_as(user)
    ok = client.patch("/api/gamification/settings", json={"daily_goal": 50})
    assert ok.status_code == 200 and ok.json()["daily"]["goal"] == 50 and ok.json()["show_on_leaderboard"] is False

    both = client.patch("/api/gamification/settings", json={"daily_goal": 20, "show_on_leaderboard": True}).json()
    assert both["daily"]["goal"] == 20 and both["show_on_leaderboard"] is True
    only_flag = client.patch("/api/gamification/settings", json={"show_on_leaderboard": False}).json()
    assert only_flag["daily"]["goal"] == 20 and only_flag["show_on_leaderboard"] is False  # the goal is left alone
    assert client.patch("/api/gamification/settings", json={}).json()["daily"]["goal"] == 20

    for bad in ({"daily_goal": 25}, {"daily_goal": 0}, {"daily_goal": -30}, {"daily_goal": "lots"},
                {"show_on_leaderboard": "maybe"}):
        r = client.patch("/api/gamification/settings", json=bad)
        assert r.status_code == 422, bad
    assert client.patch("/api/gamification/settings", content="not json",
                        headers={"Content-Type": "application/json"}).status_code == 422
    assert client.get("/api/gamification/me").json()["daily"]["goal"] == 20  # nothing invalid got through

    db.expire_all()
    profile = db.get(GamificationProfile, user.id)
    assert (profile.daily_goal, profile.show_on_leaderboard) == (20, False)
    # Changing settings is not learning: no streak day, no XP.
    me = client.get("/api/gamification/me").json()
    assert me["streak"]["count"] == 0 and me["xp_total"] == 0


def test_leaderboard_is_opt_in_anonymised_and_ranked_by_weekly_xp(client, db, user):
    asha = user  # "Asha Kumar"
    priya = make_user(db, name="Priya Sharma")
    ravi = make_user(db, name="ravi.k@example.com")
    hidden = make_user(db, name="Hidden Learner")
    lessons = doc_ids(client)

    def learn(who, how_many, opt_in):
        login_as(who)
        if opt_in:
            assert client.patch("/api/gamification/settings", json={"show_on_leaderboard": True}).status_code == 200
        for lesson in lessons[:how_many]:
            read_lesson(client, lesson)

    learn(asha, 2, True)
    learn(priya, 1, True)
    learn(ravi, 1, True)
    learn(hidden, 2, False)

    login_as(asha)
    board = client.get("/api/gamification/leaderboard").json()
    assert board["period"] == "week"
    assert [(e["rank"], e["name"], e["xp"], e["level"], e["is_me"]) for e in board["entries"]] == [
        (1, "Asha K.", 20, 1, True),
        (2, "Learner", 10, 1, False),  # an e-mail address is never shown, not even the part before the @
        (2, "Priya S.", 10, 1, False),  # a tie shares the better rank and is ordered by name
    ]
    assert board["me"] == {"rank": 1, "xp": 20, "opted_in": True}
    assert "@" not in json.dumps(board) and "Hidden" not in json.dumps(board) and "Kumar" not in json.dumps(board)

    # Someone who has not opted in is not listed, has no rank, but still sees their own weekly XP.
    login_as(hidden)
    private = client.get("/api/gamification/leaderboard").json()
    assert private["me"] == {"rank": None, "xp": 20, "opted_in": False}
    assert [e["name"] for e in private["entries"]] == ["Asha K.", "Learner", "Priya S."]
    assert not any(e["is_me"] for e in private["entries"])

    # Opting in shows up at once, sharing first place with Asha...
    assert client.patch("/api/gamification/settings", json={"show_on_leaderboard": True}).json()["show_on_leaderboard"] is True
    joined = client.get("/api/gamification/leaderboard").json()
    assert [(e["rank"], e["name"], e["is_me"]) for e in joined["entries"]] == [
        (1, "Asha K.", False), (1, "Hidden L.", True), (3, "Learner", False), (3, "Priya S.", False),
    ]
    assert joined["me"] == {"rank": 1, "xp": 20, "opted_in": True}

    # ...and opting out removes the name again.
    assert client.patch("/api/gamification/settings", json={"show_on_leaderboard": False}).status_code == 200
    gone = client.get("/api/gamification/leaderboard").json()
    assert "Hidden L." not in [e["name"] for e in gone["entries"]] and gone["me"]["rank"] is None

    login_as(ravi)
    assert client.get("/api/gamification/leaderboard").json()["me"] == {"rank": 2, "xp": 10, "opted_in": True}


# --------------------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method, path, body",
    [
        ("post", "/api/progress/lesson-view", {"module_id": M1, "lesson_id": "01-getting-started-with-python"}),
        ("post", f"/api/quiz/{M1}/submit", {"answers": {}}),
        ("post", f"/api/problems/{M1}/{EASY}/submit", {"code": "print(1)"}),
        ("post", "/api/progress/track-access", {"path": "/", "title": "Home"}),
        ("get", "/api/progress/dashboard", None),
        ("get", f"/api/progress/{M1}", None),
        ("get", "/api/gamification/me", None),
        ("get", "/api/gamification/badges", None),
        ("get", "/api/gamification/leaderboard", None),
        ("patch", "/api/gamification/settings", {"daily_goal": 50}),
    ],
)
def test_everything_requires_login(client, db, method, path, body):
    r = client.request(method.upper(), path, json=body)
    assert r.status_code == 401
    assert count(db, XPEvent) == 0 and count(db, GamificationProfile) == 0 and count(db, LessonProgress) == 0


# --------------------------------------------------------------------------------------
# Hardening (review round 1)
# --------------------------------------------------------------------------------------


def age_quiz_attempts(db, hours):
    """Move every saved quiz attempt `hours` into the past (time passing for the retry cooldown)."""
    for attempt in db.query(QuizAttempt):
        attempt.attempted_at = datetime.now(timezone.utc) - timedelta(hours=hours)
    db.commit()


def test_a_blank_quiz_followed_by_the_revealed_answers_earns_no_xp_or_badges(client, db, user, monkeypatch):
    """Submit {} once, read the answer key from the response, submit it: used to pay 85 XP, Flawless and Sharp Mind."""
    from app.services import gamification_rules as rules

    monkeypatch.setattr(g, "QUIZ_RETRY_COOLDOWN", rules.QUIZ_RETRY_COOLDOWN)
    login_as(user)
    blank = submit_quiz(client, M1, {})
    assert blank["percentage"] == 0 and blank["rewards"]["xp_gained"] == 0
    key = {r["question_id"]: r["correct_answer"] for r in blank["per_question_results"]}

    cheat = submit_quiz(client, M1, key)
    assert cheat["percentage"] == 100.0  # graded honestly...
    assert cheat["rewards"]["xp_gained"] == 0 and cheat["rewards"]["events"] == []  # ...but it pays nothing
    assert badge_ids(cheat["rewards"]) == []
    assert count(db, XPEvent, user_id=user.id, kind="quiz_perfect") == 0
    earned = {b["id"] for b in client.get("/api/gamification/badges").json()["badges"] if b["earned"]}
    assert earned == {"first-quiz"}

    # An honest retake after the cooldown is paid (the answers were learned, but a night has passed).
    age_quiz_attempts(db, hours=13)
    retake = submit_quiz(client, M1, key)["rewards"]
    assert kinds(retake)["quiz"] == 50 and kinds(retake)["quiz_perfect"] == 25
    assert {"quiz-80", "perfect-quiz"} <= set(badge_ids(retake))


def test_quiz_submits_are_rate_limited_per_learner(client, db, user, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "QUIZ_SUBMIT_RATE_LIMIT_PER_MINUTE", 3)
    login_as(user)
    for _ in range(3):
        submit_quiz(client, M1, {})
    limited = client.post(f"/api/quiz/{M1}/submit", json={"answers": {}})
    assert limited.status_code == 429
    assert count(db, QuizAttempt, user_id=user.id) == 3  # the refused call saved nothing

    other = make_user(db, name="Other Learner")
    login_as(other)
    assert client.post(f"/api/quiz/{M1}/submit", json={"answers": {}}).status_code == 200  # per learner


def test_code_submits_are_rate_limited_per_learner(client, db, user, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "CODE_SUBMIT_RATE_LIMIT_PER_MINUTE", 2)
    login_as(user)
    for _ in range(2):
        submit_code(client, M1, EASY, "print(1)")
    assert client.post(f"/api/problems/{M1}/{EASY}/submit", json={"code": "print(1)"}).status_code == 429
    assert count(db, CodeSubmission, user_id=user.id) == 2


@pytest.mark.parametrize(
    "answers",
    [
        {f"q{n}": 1 for n in range(201)},  # more answers than any quiz has questions
        {"q1": [1, 2, 3]},  # nested structures are not answers
        {"q1": {"deep": {"deeper": 1}}},
        {"q1": "x" * 501},  # megabytes of padding
        {"k" * 101: 1},
    ],
)
def test_quiz_answers_are_bounded_and_scalar(client, db, user, answers):
    login_as(user)
    r = client.post(f"/api/quiz/{M1}/submit", json={"answers": answers})
    assert r.status_code == 422
    assert count(db, QuizAttempt) == 0


def test_lessons_fired_off_in_a_burst_pay_xp_only_for_the_first(client, db, user, monkeypatch):
    """A loop over the lesson ids used to pay 10 XP each, instantly (880 XP and the epic badge in a second)."""
    from app.services import gamification_rules as rules

    monkeypatch.setattr(g, "LESSON_MIN_GAP", rules.LESSON_MIN_GAP)
    login_as(user)
    lessons = doc_ids(client)
    results = [read_lesson(client, lesson)["rewards"] for lesson in lessons]
    assert [r["xp_gained"] for r in results[:2]] == [10, 0]
    total = client.get("/api/gamification/me").json()["xp_total"]
    assert total <= 10 + 10 and total < 10 * len(lessons) / 2  # at most the first lesson (and a goal bonus)
    # The pace rule withholds XP only: every saved view is a "read" everywhere (the UI says "Read"),
    # so badges and module mastery agree with what the learner sees.
    lessons_progress = next(b for b in client.get("/api/gamification/badges").json()["badges"] if b["id"] == "lessons-10")
    assert lessons_progress["progress"]["current"] == len(lessons)
    assert count(db, LessonProgress, user_id=user.id) == len(lessons)  # the learner's own progress is saved as usual

    # A reader who spends real time is paid: the previous paid lesson is now a minute old.
    for event in db.query(XPEvent).filter_by(user_id=user.id):
        event.created_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()
    assert read_lesson(client, lessons[1])["rewards"]["xp_gained"] >= 10


def test_the_dashboard_and_the_xp_chip_show_a_living_legacy_streak_before_the_first_activity(client, db, user):
    user.streak_count = 12
    user.last_streak_update = NOW - timedelta(days=1)
    db.commit()
    login_as(user)
    assert dashboard(client)["streak_count"] == 12
    streak = client.get("/api/gamification/me").json()["streak"]
    assert (streak["count"], streak["at_risk"], streak["active_today"]) == (12, True, False)
    assert count(db, GamificationProfile) == 0  # looking creates nothing
    assert read_lesson(client, doc_ids(client)[0])["rewards"]["streak"]["count"] == 13  # and the first lesson continues it


def test_a_legacy_streak_pays_no_milestone_on_the_first_lesson(client, db, user):
    user.streak_count = 7
    user.last_streak_update = NOW
    db.commit()
    login_as(user)
    first = read_lesson(client, doc_ids(client)[0])["rewards"]
    assert kinds(first) == {"lesson": 10} and badge_ids(first) == ["first-lesson"]


def test_lowering_the_goal_through_the_endpoint_pays_the_bonus(client, db, user):
    login_as(user)
    set_goal(client, 80)
    for lesson in doc_ids(client)[:3]:
        read_lesson(client, lesson)
    r = client.patch("/api/gamification/settings", json={"daily_goal": 20})
    assert r.status_code == 200
    assert r.json()["daily"] == {"goal": 20, "xp_today": 30, "goal_met": True, "just_met": False}
    assert r.json()["xp_total"] == 40 and count(db, XPEvent, user_id=user.id, kind="daily_goal") == 1


def test_signup_rejects_blank_and_giant_names(client, db):
    base = {"email": "kid@example.com", "password": "secret-password"}
    assert client.post("/api/auth/signup", json={**base, "full_name": "B" * 100_000}).status_code == 422
    assert client.post("/api/auth/signup", json={**base, "full_name": "   "}).status_code == 422
    assert db.query(User).count() == 0
