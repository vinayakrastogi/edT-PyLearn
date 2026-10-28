"""Compact helpers for writing quiz.json files. Run tools.check_content afterwards."""
import json
from pathlib import Path
from typing import List

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"


def mcq(question: str, options: List[str], answer: int, explanation: str, concepts: List[str]) -> dict:
    return {"type": "mcq", "question": question, "options": options,
            "correct_answer": answer, "explanation": explanation, "concepts": concepts}


def tf(question: str, answer: bool, explanation: str, concepts: List[str]) -> dict:
    return {"type": "true_false", "question": question, "correct_answer": answer,
            "explanation": explanation, "concepts": concepts}


def write_quiz(module_id: str, prefix: str, title: str, questions: List[dict]) -> None:
    for i, q in enumerate(questions, start=1):
        q["id"] = f"{prefix}_q{i}"
    data = {"id": f"{module_id}-quiz", "title": title, "questions": questions}
    (CONTENT_DIR / module_id / "quiz.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"  wrote {module_id}/quiz.json ({len(questions)} questions)")
