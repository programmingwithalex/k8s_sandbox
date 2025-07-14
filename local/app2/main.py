from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI App 2"}


@app.get("/healthz")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
