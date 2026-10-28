from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.schemas.gamification import RewardSummary


class TestCase(BaseModel):
    input: Any
    expected: str


class ProblemMeta(BaseModel):
    id: str
    title: str
    concepts: List[str] = []


class ProblemDetail(BaseModel):
    id: str
    title: str
    description: str
    starter_code: str
    concepts: List[str] = []
    visible_tests: List[Dict]  # shown to user
    difficulty: str = "easy"
    hints: List[str] = []  # revealed one at a time, weakest hint first
    type: str = "function"  # "function" (call the learner's def) | "program" (stdin -> stdout)


class CodeSubmitRequest(BaseModel):
    code: str = Field(max_length=20_000)


class TestResult(BaseModel):
    test_index: int
    passed: bool
    expected: str
    actual: str
    is_hidden: bool


class CodeSubmitResponse(BaseModel):
    status: str  # PASS | FAIL | ERROR | TIMEOUT
    passed_count: int
    total_count: int
    test_results: List[TestResult]
    stdout: str
    stderr: str
    rewards: Optional[RewardSummary] = None  # null when gamification could not be recorded


class SubmissionRecord(BaseModel):
    id: int
    problem_id: str
    code: str
    status: str
    test_results: Optional[List[Dict]] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    submitted_at: datetime

    model_config = {"from_attributes": True}
