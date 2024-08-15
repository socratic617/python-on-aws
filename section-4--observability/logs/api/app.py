from fastapi import (
    FastAPI,
    Request,
)
from loguru import logger
from routes import router

logger.remove()
logger.add(lambda msg: print(msg), format="{time} | {level} | {message} | {extra}", serialize=False)


async def log_request_middleware(request: Request, call_next):
    with logger.contextualize(
        request_id=str(request.headers.get("X-Request-ID", request.url.path)),
        method=request.method,
        path=request.url.path,
        route=str(request.url.path),
    ):
        logger.info(f"Request {request.method} {request.url.path}")
        response = await call_next(request)

    return response


@router.get("/hello")
async def read_hello():
    logger.info("Handling /hello GET request")
    return {"message": "Hello, World!"}


@router.post("/echo")
async def echo_message(message: str):
    logger.info(f"Handling /echo POST request with message: {message}")
    return {"message": message}


def create_app() -> FastAPI:
    app = FastAPI()
    app.middleware("http")(log_request_middleware)
    app.include_router(router)
    logger.info("App initialized")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
