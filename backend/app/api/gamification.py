from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_tz_offset
from app.models.user import User
from app.schemas.gamification import (
    BadgeListResponse,
    GamificationSummary,
    LeaderboardResponse,
    SettingsUpdate,
)
from app.services import gamification

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/me", response_model=GamificationSummary)
def my_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tz_offset: int = Depends(get_tz_offset),
):
    return gamification.get_summary(db, current_user, tz_offset=tz_offset)


@router.get("/badges", response_model=BadgeListResponse)
def badge_catalogue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BadgeListResponse(badges=gamification.list_badges(db, current_user))


@router.get("/leaderboard", response_model=LeaderboardResponse)
def leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tz_offset: int = Depends(get_tz_offset),
):
    return gamification.get_leaderboard(db, current_user, tz_offset=tz_offset)


@router.patch("/settings", response_model=GamificationSummary)
def update_my_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tz_offset: int = Depends(get_tz_offset),
):
    return gamification.update_settings(db, current_user, payload, tz_offset=tz_offset)
