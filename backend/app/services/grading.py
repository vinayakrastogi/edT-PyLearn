from typing import List, Dict, Any
from app.services.execution import run_python_code, build_test_harness, ExecutionResult
from app.schemas.problem import TestResult


def _normalise(text: str) -> str:
    """Ignore trailing spaces per line and trailing blank lines."""
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def grade_submission(code: str, all_tests: List[Dict]) -> Dict:
    """
    Run user code against all test cases (visible + hidden).
    Returns grading result dict compatible with CodeSubmitResponse.
    Never exposes hidden test expected values to the client in detail.
    """
    test_results: List[TestResult] = []
    all_stdout_lines = []
    last_stderr = ""
    timed_out = False
    errored = False

    for i, test in enumerate(all_tests):
        test_input = test.get("input")
        expected = str(test.get("expected", "")).strip()
        is_hidden = test.get("is_hidden", False)

        if "driver" in test:
            # Class/stateful problem: append a driver script that exercises the learner's code.
            result = run_python_code(code + "\n\n# --- driver ---\n" + str(test["driver"]) + "\n")
            actual = _normalise(result.stdout)
            expected = _normalise(expected)
        elif "stdin" in test:
            # Program problem: run the whole script, feed stdin, compare stdout.
            result = run_python_code(code, stdin_input=str(test["stdin"]))
            actual = _normalise(result.stdout)
            expected = _normalise(expected)
        else:
            harness = build_test_harness(code, test_input, expected)
            result = run_python_code(harness)
            actual = result.stdout.strip()
        passed = (actual == expected) and not result.timed_out and not result.error

        if result.timed_out:
            timed_out = True
        if result.error:
            errored = True

        last_stderr = result.stderr or last_stderr
        all_stdout_lines.append(result.stdout)

        test_results.append(TestResult(
            test_index=i,
            passed=passed,
            expected=expected if not is_hidden else "***hidden***",
            actual=actual if not is_hidden else ("***" if not passed else "passed"),
            is_hidden=is_hidden,
        ))

    passed_count = sum(1 for t in test_results if t.passed)
    total_count = len(test_results)

    if timed_out:
        status = "TIMEOUT"
    elif errored and passed_count == 0:
        status = "ERROR"
    elif passed_count == total_count:
        status = "PASS"
    else:
        status = "FAIL"

    return {
        "status": status,
        "passed_count": passed_count,
        "total_count": total_count,
        "test_results": [t.model_dump() for t in test_results],
        "stdout": "\n".join(all_stdout_lines),
        "stderr": last_stderr,
    }


def grade_quiz(questions_with_answers: List[Dict], user_answers: Dict[str, Any]) -> Dict:
    """
    Grade a quiz submission.
    questions_with_answers: full question dicts from content file (including 'correct' field)
    user_answers: {question_id: answer_value}
    """
    per_question_results = []
    correct_count = 0

    for q in questions_with_answers:
        qid = q["id"]
        user_ans = user_answers.get(qid)
        correct_ans = q.get("correct_answer") if "correct_answer" in q else q.get("correct")
        is_correct = (user_ans == correct_ans)
        if is_correct:
            correct_count += 1

        per_question_results.append({
            "question_id": qid,
            "correct": is_correct,
            "concepts": q.get("concepts", []),
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "explanation": q.get("explanation"),
        })

    max_score = len(questions_with_answers)
    score = float(correct_count)
    percentage = round((score / max_score * 100) if max_score > 0 else 0, 1)

    return {
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "per_question_results": per_question_results,
    }
