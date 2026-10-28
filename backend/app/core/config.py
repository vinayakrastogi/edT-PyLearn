from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
from typing import List, Literal
from urllib.parse import urlsplit


class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "test", "production"] = "development"
    # Database
    DATABASE_URL: str = "postgresql://edt_user:edt_password@localhost:5432/edt_db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def use_installed_postgres_driver(cls, value):
        # SQLAlchemy 2.1 changed the default PostgreSQL driver; this project installs psycopg2.
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg2://", 1)
        return value

    # Auth
    SECRET_KEY: str = "change-me-to-a-long-random-string-in-production-minimum-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    COOKIE_DOMAIN: str | None = None  # host-only by default
    TRUSTED_HOSTS: List[str] = ["*"]

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    # Content
    CONTENT_DIR: str = "../content"

    # OAuth
    GOOGLE_CLIENT_ID: str = "replace_me_with_google_client_id"
    GOOGLE_CLIENT_SECRET: str = "replace_me_with_google_client_secret"
    SESSION_SECRET: str = "change-me-to-a-long-random-string-for-session-middleware"

    # AI
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # Local subprocesses are for development. Hosted backends use a separate runner.
    SANDBOX_MODE: Literal["local", "docker", "remote", "disabled"] = "local"
    SANDBOX_DOCKER_IMAGE: str = "pylearn-sandbox:latest"
    SANDBOX_TIMEOUT_SECONDS: int = Field(default=5, ge=1, le=30)
    SANDBOX_MAX_CONCURRENT: int = Field(default=2, ge=1, le=8)
    SANDBOX_RUNNER_URL: str = ""
    SANDBOX_RUNNER_KEY: str = ""
    RUN_RATE_LIMIT_PER_MINUTE: int = 30
    # Shared key for the public code-runner demo API (POST /api/public/run)
    PUBLIC_API_KEY: str = "pylearn-demo"
    PUBLIC_API_ENABLED: bool = True
    # Independent LifeAdmin service. A blank key leaves lesson notes disabled.
    LIFEADMIN_API_URL: str = "http://127.0.0.1:8001"
    LIFEADMIN_API_KEY: str = ""
    LIFEADMIN_TIMEOUT_SECONDS: float = 8.0
    # Unique per PyLearn installation if several installations use one LifeAdmin service.
    LIFEADMIN_CLIENT_ID: str = "pylearn"
    FRONTEND_URL: str = "http://localhost:5173"
    # Graded submissions per learner per minute (every one is stored and graded)
    QUIZ_SUBMIT_RATE_LIMIT_PER_MINUTE: int = 10
    CODE_SUBMIT_RATE_LIMIT_PER_MINUTE: int = 20
    # Optional single-origin production deployment; avoids third-party cookie blocking.
    SERVE_FRONTEND: bool = False
    FRONTEND_DIST_DIR: str = "../frontend/dist"

    @model_validator(mode="after")
    def validate_deployment(self):
        frontend = urlsplit(self.FRONTEND_URL)
        if (frontend.scheme not in {"http", "https"} or not frontend.hostname or frontend.username
                or frontend.query or frontend.fragment or frontend.path not in {"", "/"}):
            raise ValueError("FRONTEND_URL must be an absolute browser origin without a path.")
        for origin in self.BACKEND_CORS_ORIGINS:
            parts = urlsplit(origin)
            if (parts.scheme not in {"http", "https"} or not parts.hostname or parts.username
                    or parts.path or parts.query or parts.fragment or "*" in origin):
                raise ValueError("BACKEND_CORS_ORIGINS must contain exact origins without paths or wildcards.")
        if self.COOKIE_SAMESITE == "none" and not self.COOKIE_SECURE:
            raise ValueError("SameSite=None requires COOKIE_SECURE=true.")
        if self.SANDBOX_MODE == "remote":
            parts = urlsplit(self.SANDBOX_RUNNER_URL)
            if (parts.scheme not in {"http", "https"} or not parts.hostname or parts.username
                    or parts.query or parts.fragment or len(self.SANDBOX_RUNNER_KEY) < 32):
                raise ValueError("Remote execution requires SANDBOX_RUNNER_URL and a runner key of at least 32 characters.")
        if self.ENVIRONMENT == "production":
            for name in ("SECRET_KEY", "SESSION_SECRET"):
                value = getattr(self, name)
                if len(value) < 32 or value.startswith(("change-me", "replace_me")):
                    raise ValueError(f"Production requires a random {name} of at least 32 characters.")
            if not self.COOKIE_SECURE:
                raise ValueError("Production requires COOKIE_SECURE=true.")
            if frontend.scheme != "https":
                raise ValueError("Production FRONTEND_URL must use HTTPS.")
            if not self.TRUSTED_HOSTS or any("*" in host for host in self.TRUSTED_HOSTS):
                raise ValueError("Production requires explicit TRUSTED_HOSTS.")
            if any(not origin.startswith("https://") for origin in self.BACKEND_CORS_ORIGINS):
                raise ValueError("Production CORS origins must use HTTPS.")
            if self.SANDBOX_MODE == "local":
                raise ValueError("Production cannot execute learner code in local subprocesses. Use remote, docker or disabled.")
            if self.SANDBOX_MODE == "remote" and not self.SANDBOX_RUNNER_URL.startswith("https://"):
                raise ValueError("Production remote execution requires HTTPS.")
            if self.PUBLIC_API_ENABLED and (len(self.PUBLIC_API_KEY) < 32 or self.PUBLIC_API_KEY == "pylearn-demo"):
                raise ValueError("Disable PUBLIC_API_ENABLED or configure a random PUBLIC_API_KEY of at least 32 characters.")
        return self

    model_config = {"env_file": [".env", "../.env"], "extra": "ignore"}


settings = Settings()
