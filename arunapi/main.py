from fastapi import FastAPI, Request, Response

from . import __version__
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
