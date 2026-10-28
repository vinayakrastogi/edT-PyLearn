from pathlib import PurePosixPath

from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles


class SPAStaticFiles(StaticFiles):
    """Serve React routes without disguising missing API endpoints or assets as HTML."""
    async def get_response(self, path, scope):
        if path == "api" or path.startswith("api/"):
            raise HTTPException(404)
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code != 404 or PurePosixPath(path).suffix or path.startswith("assets/"):
                raise
            return await super().get_response("index.html", scope)
