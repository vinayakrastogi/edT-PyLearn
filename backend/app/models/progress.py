from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean,
    ForeignKey, Float, func, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import JSONB
import enum

from app.core.database import Base


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(String, nullable=False, index=True)
    lesson_id = Column(String, nullable=False, index=True)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_complete = Column(Boolean, default=True, nullable=False)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(String, nullable=False, index=True)
    quiz_id = Column(String, nullable=False, index=True)
    # answers: {question_id: answer_value}
    answers = Column(JSONB, nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Integer, nullable=False)
    # per_question_results: [{question_id, correct, concepts, user_answer, correct_answer}]
    per_question_results = Column(JSONB, nullable=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SubmissionStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(String, nullable=False, index=True)
    problem_id = Column(String, nullable=False, index=True)
    code = Column(Text, nullable=False)
    status = Column(SAEnum(SubmissionStatus), nullable=False)
    # test_results: [{test_index, passed, expected, actual}]
    test_results = Column(JSONB, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
