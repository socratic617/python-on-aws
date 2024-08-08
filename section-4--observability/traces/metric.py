from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

from aws_embedded_metrics import MetricsLogger
from aws_embedded_metrics.storage_resolution import StorageResolution
from aws_embedded_metrics.config import get_config
from aws_embedded_metrics.logger.metrics_logger_factory import create_metrics_logger

# metrics config
config = get_config()

config.service_name = "fastapi-service"
config.log_group_name = "FastAPIAppMetrics"
config.environment = "local"


@asynccontextmanager
async def make_metrics_logger() -> AsyncGenerator[MetricsLogger, None]:
    metrics = create_metrics_logger()
    try:
        yield metrics
    finally:
        await metrics.flush()


async def log_metric():
    async with make_metrics_logger() as metrics:
        metrics.put_dimensions({"ServiceName": "fastapi-service"})
        metrics.put_metric(
            "CustomMetric",
            1,
            "Count",
            storage_resolution=StorageResolution.STANDARD,
        )


asyncio.run(log_metric())
