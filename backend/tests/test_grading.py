from app.services.grading import grade_quiz, grade_submission
from app.services.execution import run_python_code

FUNC = "def add(a, b):\n    return a + b\n"


def test_function_problem_pass_and_fail():
    ok = grade_submission(FUNC, [{"input": [1, 2], "expected": "3"}])
    assert ok["status"] == "PASS"
    bad = grade_submission("def add(a, b):\n    return a - b\n", [{"input": [1, 2], "expected": "3"}])
    assert bad["status"] == "FAIL"


def test_hidden_tests_are_masked():
    res = grade_submission(FUNC, [{"input": [1, 2], "expected": "3", "is_hidden": True}])
    assert res["test_results"][0]["expected"] == "***hidden***"


def test_program_problem_uses_stdin_and_ignores_trailing_space():
    code = "name = input()\nprint('Hi ' + name + '!  ')\n"
    res = grade_submission(code, [{"stdin": "Ada\n", "expected": "Hi Ada!"}])
    assert res["status"] == "PASS"


def test_driver_problem_for_classes():
    code = "class C:\n    def __init__(self):\n        self.n = 0\n    def inc(self):\n        self.n += 1\n"
    res = grade_submission(code, [{"driver": "c = C()\nc.inc()\nc.inc()\nprint(c.n)", "expected": "2"}])
    assert res["status"] == "PASS"


def test_timeout_is_reported():
    res = run_python_code("while True:\n    pass\n")
    assert res.timed_out


def test_learner_code_cannot_see_server_secrets(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "super-secret")
    res = run_python_code("import os\nprint(os.environ.get('GROQ_API_KEY'))")
    assert res.stdout.strip() == "None"


def test_output_is_truncated():
    res = run_python_code("print('x' * 100000)")
    assert len(res.stdout) < 21000


def test_quiz_grading_returns_explanations():
    qs = [
        {"id": "a", "type": "mcq", "options": ["x", "y"], "correct_answer": 1, "explanation": "because", "concepts": ["c"]},
        {"id": "b", "type": "true_false", "correct_answer": True, "explanation": "yes", "concepts": ["c"]},
    ]
    res = grade_quiz(qs, {"a": 1, "b": False})
    assert res["score"] == 1
    assert res["per_question_results"][0]["explanation"] == "because"
    assert res["per_question_results"][1]["correct"] is False
