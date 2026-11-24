import hashlib
import hmac
from typing import Annotated

from botocore.exceptions import ClientError
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from mangum import Mangum

from gpu_compare import sessions
from gpu_compare.benchmarks import api as benchmarks_api
from gpu_compare.benchmarks import service as benchmarks_service
from gpu_compare.config import settings
from gpu_compare.db import transaction

app = FastAPI(
    title="GPU Compare API",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)


class BodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        size = 0

        async def limited_receive():
            nonlocal size
            message = await receive()
            size += len(message.get("body", b""))
            if size > 5 * 1024 * 1024:
                raise HTTPException(413, "Anfrage ist zu groß.")
            return message

        await self.app(scope, limited_receive, send)


app.add_middleware(BodyLimit)


def signature(session, purpose):
    return hmac.new(
        settings().session_secret.get_secret_value().encode(),
        (purpose + ":" + session).encode(),
        hashlib.sha256,
    ).hexdigest()


@app.middleware("http")
async def guards(request: Request, call_next):
    machine = request.method == "POST" and benchmarks_api.RUNNER_PATH.fullmatch(request.url.path)
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not machine:
        origin = request.headers.get("origin")
        if origin and origin != settings().public_origin:
            return JSONResponse({"detail": "Diese Herkunft ist nicht erlaubt."}, status_code=403)
        if not origin and settings().public_demo:
            return JSONResponse({"detail": "Origin-Header erforderlich."}, status_code=403)
        size = request.headers.get("content-length")
        if size and (not size.isdigit() or int(size) > 5 * 1024 * 1024):
            return JSONResponse({"detail": "Anfrage ist zu groß."}, status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(ValueError)
async def invalid(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=422)


@app.exception_handler(PermissionError)
async def forbidden(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=401)


@app.exception_handler(LookupError)
async def missing(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=404)


@app.exception_handler(ClientError)
async def aws_unavailable(request, exc):
    return JSONResponse(
        {
            "detail": "Die Demo wird gestartet oder ein Dienst ist vorübergehend nicht verfügbar. Bitte kurz warten."
        },
        status_code=503,
        headers={"Retry-After": "5"},
    )


def session(request: Request):
    cookie = request.cookies.get("gpu_compare_session", "")
    identifier, _, mac = cookie.partition(".")
    if not identifier or not hmac.compare_digest(signature(identifier, "cookie"), mac):
        raise PermissionError("Bitte zuerst eine Demo-Sitzung starten.")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        if not hmac.compare_digest(
            signature(identifier, "csrf"), request.headers.get("x-csrf-token", "")
        ):
            raise HTTPException(403, "Ungültiges Sitzungstoken.")
    with transaction() as db:
        sessions.active_session(db, identifier)
    return identifier


Session = Annotated[str, Depends(session)]


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/demo-sessions")
def new_session(response: Response):
    identifier = sessions.create_session()
    response.set_cookie(
        "gpu_compare_session",
        identifier + "." + signature(identifier, "cookie"),
        max_age=86400,
        httponly=True,
        secure=settings().public_demo,
        samesite="lax",
        path="/",
    )
    return {"csrf_token": signature(identifier, "csrf")}


@app.get("/api/demo-sessions/current")
def current_session(s: Session):
    return {"csrf_token": signature(s, "csrf")}


@app.delete("/api/demo-sessions/current")
def delete_session(s: Session, response: Response):
    with transaction() as db:
        benchmarks_service.scrub_sessions(db, s)
        db.execute("DELETE FROM sessions WHERE id=:id", {"id": s})
    response.delete_cookie("gpu_compare_session", path="/")
    return {"deleted": True}


app.include_router(benchmarks_api.router(session))
app.include_router(benchmarks_api.runner_router)
handler = Mangum(app, lifespan="off")
