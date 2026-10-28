from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.web_security import CookieOriginMiddleware
from app.services.execution import SandboxUnavailable
from app.api import auth, modules, quiz, problems, progress, generate, classrooms, run, gamification, public_run, notes

app = FastAPI(
    title="Python Learning Platform API",
)

from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    https_only=settings.COOKIE_SECURE,
    same_site=settings.COOKIE_SAMESITE,
)

app.add_middleware(CookieOriginMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def public_api_cors(request, call_next):
    """The public runner is callable from any origin (it uses an API key, not cookies)."""
    if request.url.path != "/api/public/run":
        return await call_next(request)
    from fastapi.responses import Response
    resp = Response(status_code=204) if request.method == "OPTIONS" else await call_next(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    # This endpoint uses API keys, so it never supports credentialed CORS.
    if "Access-Control-Allow-Credentials" in resp.headers:
        del resp.headers["Access-Control-Allow-Credentials"]
    return resp


if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)


@app.exception_handler(SandboxUnavailable)
async def unavailable_runner(request, exc):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


app.include_router(auth.router)
app.include_router(modules.router)
app.include_router(quiz.router)
app.include_router(problems.router)
app.include_router(progress.router)
app.include_router(generate.router)
app.include_router(classrooms.router)
app.include_router(run.router)
app.include_router(gamification.router)
app.include_router(public_run.router)
app.include_router(notes.router)


@app.get("/health")
def health():
    return {"status": "ok"}


if settings.SERVE_FRONTEND:
    from app.core.spa import SPAStaticFiles
    app.mount("/", SPAStaticFiles(directory=settings.FRONTEND_DIST_DIR, html=True), name="frontend")
