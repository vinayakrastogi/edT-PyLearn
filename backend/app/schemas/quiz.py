import math
from pydantic import BaseModel, field_validator
from typing import List, Any, Optional, Dict
from datetime import datetime

from app.schemas.gamification import RewardSummary


class QuestionBase(BaseModel):
    id: str
    type: str  # discriminator: "mcq" | "true_false"
    question: str
    concepts: List[str] = []


class MCQQuestion(QuestionBase):
    type: str = "mcq"
    options: List[str]
    # correct index is NOT included — stripped before sending to client


class TrueFalseQuestion(QuestionBase):
    type: str = "true_false"
    # correct answer is NOT included


class QuizResponse(BaseModel):
    id: str
    module_id: str
    title: str
    questions: List[Dict]  # mixed types, correct answer stripped


MAX_QUIZ_ANSWERS = 200  # far more than any quiz has questions
MAX_ANSWER_TEXT = 500


class QuizSubmitRequest(BaseModel):
    answers: Dict[str, Any]  # {question_id: answer_value}

    @field_validator("answers")
    @classmethod
    def _bounded_answers(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        # Every submit is stored, so the payload is capped: answers are small scalars (an option
        # index, true/false or a short text), never nested structures or megabytes of padding.
        if len(v) > MAX_QUIZ_ANSWERS:
            raise ValueError(f"at most {MAX_QUIZ_ANSWERS} answers")
        for key, value in v.items():
            if len(key) > 100:
                raise ValueError("question id too long")
            if value is not None and not isinstance(value, (bool, int, float, str)):
                raise ValueError("answers must be numbers, true/false or text")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("answers must be finite numbers")  # NaN/Infinity cannot be stored as JSON
            if isinstance(value, str) and len(value) > MAX_ANSWER_TEXT:
                raise ValueError("answer text too long")
        return v


class QuestionResult(BaseModel):
    question_id: str
    correct: bool
    concepts: List[str]
    user_answer: Any
    correct_answer: Any
    explanation: Optional[str] = None


class QuizSubmitResponse(BaseModel):
    score: float
    max_score: int
    percentage: float
    per_question_results: List[QuestionResult]
    rewards: Optional[RewardSummary] = None  # null when gamification could not be recorded


class QuizAttemptRecord(BaseModel):
    id: int
    quiz_id: str
    score: float
    max_score: int
    percentage: float
    per_question_results: List[Dict]
    attempted_at: datetime

    model_config = {"from_attributes": True}
