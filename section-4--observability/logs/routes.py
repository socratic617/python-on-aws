from fastapi import APIRouter
from loguru import logger

router = APIRouter()

@router.get("/hello")
async def read_hello():
    logger.info("Handling /hello GET request")
    return {"message": "Hello, World!"}

@router.post("/echo")
async def echo_message(message: str):
    logger.info(f"Handling /echo POST request with message: {message}")
    return {"message": message}
