from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from aws_embedded_metrics import MetricsLogger
from aws_embedded_metrics.config import get_config
from aws_embedded_metrics.logger.metrics_logger_factory import create_metrics_logger
from aws_xray_sdk.core import (
    patch_all,
    xray_recorder,
)
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)
from aws_xray_sdk.core.models.segment import Segment

# Patch all libraries to be instrumented by AWS X-Ray
patch_all()

# trace config
xray_recorder.configure(
    context_missing="RUNTIME_ERROR",
    # sampling=True,
    # sampling_rules={
    #     "version": 2,
    #     "rules": [],
    #     "default": {"fixed_target": 1, "rate": 1.0},
    # },
)

app = FastAPI(docs_url="/")

@app.middleware("http")
async def record_xray_segment(request: Request, call_next):
    async with xray_recorder.in_segment_async("FastAPI Segment") as segment:
        segment: Segment
        response = None
        try:
            response = await call_next(request)
        except Exception as e:
            segment.put_annotation("error", str(e))
            raise e
        return response


@asynccontextmanager
async def make_metrics_logger() -> AsyncGenerator[MetricsLogger, None]:
    metrics = create_metrics_logger()

    # prevent default setting of ServiceName, LogGroup, and ServiceType as dimensions on the metrics
    metrics.reset_dimensions(use_default=False)

    try:
        yield metrics
    finally:
        await metrics.flush()


@app.get("/httpbin")
async def call_httpbin():
    with xray_recorder.in_subsegment("httpbin"):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://httpbin.org/get")
            return response.json()


@app.get("/error")
async def return_error():
    raise HTTPException(status_code=500, detail="This is an error!")


@app.get("/custom_metric")
async def send_custom_metric():
    async with make_metrics_logger() as metrics:
        metrics.set_property(key="ExampleProperty", value="ExampleValue")
        metrics.put_metric("CustomMetric2", 1, "Count")
    return {"message": "Custom metric sent"}
