import uvicorn


def run_dev():
    uvicorn.run("arunapi.main:app", host="0.0.0.0", port=8000, reload=True)
