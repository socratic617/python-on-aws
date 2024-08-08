from loguru import logger
import json     # <!- add this line
import sys

# Add the following function
def serialize(record):
    subset = {
            "level": record["level"].name,
            "timestamp": record["time"].timestamp(),
            "message": record["message"]}
    return json.dumps(subset)

# Add the following function
def formatter(record):
    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]}\n"

logger.remove(0)
logger.add(sys.stderr, format=formatter)   # <!-

logger.error("This is  an error message.")
