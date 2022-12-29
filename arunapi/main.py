import logging

from fastapi import FastAPI, Request, Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from .cache import Cache
from .routers import refuse
from .settings import Settings

settings = Settings()

app = FastAPI(**settings.app.dict())
app.state.settings = settings

settings.telemetry(app.state.settings)
LoggingInstrumentor().instrument(set_logging_format=True)


@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(refuse.router)


@app.on_event("startup")
async def init_cache():
    cache = Cache(settings.cache)
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
    environment: str = app.state.settings.environment
    if cache_health != "OK":
        response.status_code = 500
    return {"cache": cache_health, "environment": environment}


FastAPIInstrumentor.instrument_app(app)
