from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.schemas.gamification import RewardSummary


class LessonViewRequest(BaseModel):
    module_id: str
    lesson_id: str


class TrackAccessRequest(BaseModel):
    path: str
    title: str


class LessonProgressRecord(BaseModel):
    lesson_id: str
    viewed_at: datetime
    is_complete: bool
    rewards: Optional[RewardSummary] = None  # null when gamification could not be recorded

    model_config = {"from_attributes": True}


class ModuleProgressSummary(BaseModel):
    module_id: str
    total_docs: int
    docs_read: int
    quiz_attempts: int
    best_quiz_score: Optional[float] = None
    total_problems: int
    problems_solved: int
    completion_percentage: float
    viewed_docs: list[str] = []
    passed_problems: list[str] = []


class ConceptMastery(BaseModel):
    concept: str
    correct: int
    total: int
    percentage: float


class DashboardResponse(BaseModel):
    modules: list[ModuleProgressSummary]
    streak_count: int
    mastery_stats: list[ConceptMastery]
