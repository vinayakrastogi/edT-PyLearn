"""Origin checks for cookie-authenticated mutations, including cross-site deployments."""
from urllib.parse import urlsplit

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import settings


class CookieOriginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if (request.method not in {"GET", "HEAD", "OPTIONS"}
                and request.url.path.startswith("/api/")
                and request.url.path != "/api/public/run"):
            allowed = {*settings.BACKEND_CORS_ORIGINS, settings.FRONTEND_URL.rstrip("/"),
                       str(request.base_url).rstrip("/")}
            origin = request.headers.get("origin")
            referer = request.headers.get("referer")
            if not origin and referer:
                parts = urlsplit(referer)
                origin = f"{parts.scheme}://{parts.netloc}"
            if origin:
                if origin not in allowed:
                    return JSONResponse({"detail": "Request origin is not allowed."}, status_code=403)
            elif (request.cookies.get("access_token")
                  and request.headers.get("x-csrf-protection") != "1"):
                # Non-browser tools may send this header. Cross-origin browsers
                # must pass the configured CORS preflight before they can send it.
                return JSONResponse({"detail": "Send Origin or X-CSRF-Protection: 1."}, status_code=403)
        return await call_next(request)
