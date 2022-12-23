import logging

from fastapi import FastAPI, Request, Response

from . import __version__
from .cache import Cache
from .routers import refuse

app = FastAPI(
    title="Arun DC API",
    description="The missing API for Arun District Council services",
    version=__version__,
    contact={
        "name": "Tom Whitwell",
        "url": "https://whi.tw/ell",
        "email": "arunapi@mail.whi.tw",
    },
    docs_url="/",
)


@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(refuse.router)


@app.on_event("startup")
async def init_cache():
    cache = Cache()
    app.state.cache = cache


@app.on_event("startup")
async def disable_logging_health_endpoint():
    uvicorn_access_logger = logging.getLogger("uvicorn.access")

    class HealthcheckFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            query_string: str = record.args[2]
            status_code: int = record.args[4]
            return not (query_string == "/health" and status_code == 200)

    uvicorn_access_logger.addFilter(HealthcheckFilter())


@app.get("/health", include_in_schema=False)
async def health_endpoint(response: Response):
    cache: Cache = app.state.cache
    cache_health = await cache.health()
    if cache_health != "OK":
        response.status_code = 500
    return {"cache": cache_health}
