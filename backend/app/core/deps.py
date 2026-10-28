from typing import Generator, Optional

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    access_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    if not access_token:
        raise credentials_exception

    user_id = decode_access_token(access_token)
    if not user_id:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise credentials_exception
    return user


def get_tz_offset(x_tz_offset: Optional[str] = Header(default=None)) -> int:
    """
    The learner's UTC offset in minutes as sent by the browser (`X-TZ-Offset: <minutes>`, i.e.
    JavaScript's `new Date().getTimezoneOffset()`: UTC minus local, IST = -330).

    Clamped to [-840, 840]; missing or invalid values fall back to 0 (UTC). Never raises.
    """
    if x_tz_offset is None:
        return 0
    try:
        minutes = int(x_tz_offset.strip())
    except (ValueError, AttributeError):
        return 0
    return max(-840, min(840, minutes))


def require_faculty(user: User = Depends(get_current_user)) -> User:
    """Only faculty accounts may manage or generate content."""
    if user.role != "faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faculty access required",
        )
    return user
