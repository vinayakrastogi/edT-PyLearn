from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.responses import RedirectResponse

from app.core.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, UserResponse, clean_full_name

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
        max_age=COOKIE_MAX_AGE,
        secure=settings.COOKIE_SECURE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))
    _set_auth_cookie(response, token)
    return user


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(user.id))
    _set_auth_cookie(response, token)
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/", domain=settings.COOKIE_DOMAIN,
                           secure=settings.COOKIE_SECURE, httponly=True, samesite=settings.COOKIE_SAMESITE)
    # Clear cookies issued by older localhost-only versions as well.
    if settings.ENVIRONMENT != "production":
        response.delete_cookie(COOKIE_NAME, domain="localhost", path="/")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/google/login")
async def google_login(request: Request):
    # This redirects the user to the Google consent screen
    redirect_uri = request.url_for('google_callback')
    # If testing locally, ensure http vs https matches the redirect_uri configured in Google Console
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error.error}")
    
    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
    
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")
    
    # Check if user already exists (by google_id or email)
    user = db.query(User).filter(
        (User.google_id == user_info["sub"]) | (User.email == email)
    ).first()
    
    if user:
        # Update google_id and avatar if missing (linking account)
        if not user.google_id:
            user.google_id = user_info["sub"]
        if not user.avatar_url and user_info.get("picture"):
            user.avatar_url = user_info["picture"]
        db.commit()
    else:
        # Create new user
        user = User(
            email=email,
            full_name=clean_full_name(user_info.get("name") or "") or "Unknown User",
            google_id=user_info["sub"],
            avatar_url=user_info.get("picture"),
            hashed_password=None,  # No password for OAuth
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create standard JWT cookie
    jwt_token = create_access_token(str(user.id))
    
    # Redirect to frontend dashboard with cookie
    frontend_url = f"{settings.FRONTEND_URL.rstrip('/')}/dashboard"
    response = RedirectResponse(url=frontend_url)
    _set_auth_cookie(response, jwt_token)
    return response
