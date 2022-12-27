import os

import uvicorn

from . import __version__


def run_dev():
    os.environ["ENVIRONMENT"] = "dev"
    uvicorn.run("arunapi.main:app", host="0.0.0.0", port=8000, reload=True)

def current_version():
    print(__version__)
