from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

MAX_FULL_NAME_LENGTH = 100


def clean_full_name(value: str) -> str:
    """Trim and cap a display name (it is shown to other learners on the leaderboard)."""
    return " ".join(str(value).split())[:MAX_FULL_NAME_LENGTH]


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = Field(min_length=1, max_length=MAX_FULL_NAME_LENGTH)
    role: str = "student"  # "student" or "faculty", defaults to student

    @field_validator("full_name")
    @classmethod
    def _tidy_full_name(cls, v: str) -> str:
        cleaned = clean_full_name(v)
        if not cleaned:
            raise ValueError("full_name must not be blank")
        return cleaned


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    last_accessed_path: str | None = None
    last_accessed_title: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
