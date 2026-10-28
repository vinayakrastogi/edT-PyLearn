from sqlalchemy import (
    JSON, Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, String,
    UniqueConstraint, false, func, text,
)

from app.core.database import Base


class GamificationProfile(Base):
    """One row per learner: cached XP total, streak extras, daily goal and leaderboard opt-in."""

    __tablename__ = "gamification_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    # Cached sum of xp_events.amount, only ever changed with `xp_total = xp_total + :amount`
    xp_total = Column(Integer, nullable=False, default=0, server_default=text("0"))
    longest_streak = Column(Integer, nullable=False, default=0, server_default=text("0"))
    streak_freezes = Column(Integer, nullable=False, default=0, server_default=text("0"))  # 0..2
    last_active_date = Column(Date, nullable=True)  # learner's local date of the last qualifying activity
    daily_goal = Column(Integer, nullable=False, default=30, server_default=text("30"))
    daily_xp = Column(Integer, nullable=False, default=0, server_default=text("0"))  # excludes the goal bonus
    daily_xp_date = Column(Date, nullable=True)  # local date `daily_xp` belongs to
    show_on_leaderboard = Column(Boolean, nullable=False, default=False, server_default=false())
    # The UTC offset (minutes, as the browser reports it) the learner's local dates are computed
    # with, and when it last changed. A client-supplied header is only believed to change this
    # rarely, so it cannot be used to forge extra local dates (see gamification._resolve_offset).
    tz_offset = Column(Integer, nullable=True)
    tz_changed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class XPEvent(Base):
    """
    The XP ledger. The unique (user_id, kind, ref_key) constraint is what makes awarding idempotent:
    "insert the event; if the constraint rejects it, it was already awarded".
    """

    __tablename__ = "xp_events"
    __table_args__ = (
        UniqueConstraint("user_id", "kind", "ref_key", name="uq_xp_events_user_kind_ref"),
        Index("ix_xp_events_user_created", "user_id", "created_at"),
        # The weekly leaderboard filters on created_at alone (no user_id), which the index above cannot serve.
        Index("ix_xp_events_created", "created_at"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    kind = Column(String(32), nullable=False)
    ref_key = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    local_date = Column(Date, nullable=False)  # the learner's local date when it was earned
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badges_user_badge"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = Column(String(64), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
