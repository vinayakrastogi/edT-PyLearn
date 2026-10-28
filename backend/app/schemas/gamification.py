"""
Gamification API contract (see GAMIFICATION.md at the repository root).

These models are the single source of truth for the JSON shapes. The TypeScript mirror lives in
frontend/src/types/gamification.ts and MUST be kept identical.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ALLOWED_DAILY_GOALS = (20, 30, 50, 80)


class BadgeProgress(BaseModel):
    current: int
    target: int


class BadgeInfo(BaseModel):
    id: str
    name: str
    description: str
    icon: str  # kebab-case icon key from frontend/src/lib/icons.tsx ICONS, e.g. "trophy"
    category: str  # learning | quizzes | coding | streaks | modules | levels
    rarity: str  # common | rare | epic | legendary
    earned: bool = False
    earned_at: Optional[datetime] = None
    progress: BadgeProgress


class RewardEvent(BaseModel):
    kind: str
    label: str  # human readable, e.g. "Lesson read"
    amount: int


class StreakInfo(BaseModel):
    count: int
    longest: int
    freezes: int
    extended: bool = False  # this activity moved the streak forward today
    used_freeze: bool = False  # a streak freeze was spent to keep the streak alive
    milestone: Optional[int] = None  # e.g. 7 when the 7-day milestone was just reached
    broken_from: Optional[int] = None  # the old streak length if this activity restarted it
    active_today: bool = True
    at_risk: bool = False  # (summary only) had activity yesterday but none yet today


class DailyInfo(BaseModel):
    goal: int
    xp_today: int
    goal_met: bool
    just_met: bool = False  # this activity pushed the day over the goal


class RewardSummary(BaseModel):
    """Returned (as `rewards`) by lesson-view, quiz submit and problem submit."""

    xp_gained: int
    events: List[RewardEvent]
    total_xp: int
    level: int
    previous_level: int
    level_title: str
    level_up: bool
    xp_into_level: int
    xp_for_next_level: int  # XP needed to cover the whole current level (denominator of the bar)
    streak: StreakInfo
    new_badges: List[BadgeInfo]
    daily: DailyInfo


class WeeklyPoint(BaseModel):
    date: str  # YYYY-MM-DD in the learner's local time
    xp: int


class RecentEvent(BaseModel):
    kind: str
    label: str
    amount: int
    created_at: datetime


class GamificationSummary(BaseModel):
    xp_total: int
    level: int
    level_title: str
    xp_into_level: int
    xp_for_next_level: int
    next_level_xp: int  # cumulative XP at which the next level starts
    streak: StreakInfo
    daily: DailyInfo
    weekly: List[WeeklyPoint]  # 7 entries, oldest first, ending today
    badges_earned: int
    badges_total: int
    recent_badges: List[BadgeInfo]  # up to 4, newest first
    recent_events: List[RecentEvent]  # up to 8, newest first
    show_on_leaderboard: bool


class BadgeListResponse(BaseModel):
    badges: List[BadgeInfo]


class LeaderboardEntry(BaseModel):
    rank: int
    name: str  # anonymised: first name + last initial, e.g. "Asha K."
    xp: int  # XP earned in the last 7 days
    level: int
    is_me: bool = False


class LeaderboardMe(BaseModel):
    rank: Optional[int] = None  # None when not opted in
    xp: int
    opted_in: bool


class LeaderboardResponse(BaseModel):
    period: str = "week"
    entries: List[LeaderboardEntry]
    me: LeaderboardMe


class SettingsUpdate(BaseModel):
    # Strict on purpose: a misspelled key ("dailyGoal") or a coerced value ("yes" -> true, which would
    # opt a child in to a public leaderboard) must be a 422, never a silent 200.
    model_config = ConfigDict(extra="forbid", strict=True)

    daily_goal: Optional[int] = None
    show_on_leaderboard: Optional[bool] = None

    @field_validator("daily_goal")
    @classmethod
    def _valid_goal(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in ALLOWED_DAILY_GOALS:
            raise ValueError(f"daily_goal must be one of {ALLOWED_DAILY_GOALS}")
        return v

    @model_validator(mode="after")
    def _no_explicit_null(self) -> "SettingsUpdate":
        # `{}` means "change nothing"; an explicit null is a client bug, not a silent no-op.
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self
