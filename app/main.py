import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse

from app import models  # noqa: F401  (registers the tables)
from app.api import accounts, auth
from app.core.exceptions import AppError
from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger("bank")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Basic Banking API",
    description="Register, log in, deposit, withdraw and transfer money.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
)


@app.get("/docs", include_in_schema=False)
async def swagger_ui():
    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
    )
    html = response.body.decode("utf-8").replace(
        "</head>",
        "<style>body { background-color: #fff0f5; }</style></head>",
    )
    return HTMLResponse(html)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}, headers=headers
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")  # full details only in the server log
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router)
app.include_router(accounts.router)
