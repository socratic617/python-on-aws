"""
Why collect monitoring data? Because by the time you need it, it's too late to get it.


Metrics - something went wrong
Logs - how it happened (root cause)
Traces - birds-eye view: where did it happen, what parts of the system are involved/affected, also profiling info

profiling (latency), error counts/rates,  

0. have an overview - show how the data types fit together and what we will build
  - "single pane of glass", massively distributed systems, etc.
  - talk about metrics, logs, and traces in advance
  - show the dashboard, alerts, and other UI's that we're going to set up
    so they have a mental framework as we go deeper
  - describe the workflow
    1. an alarm tells you something is wrong
    2. you check a dashboard and consoles
    3. you use logs to identify root cause
    4. you use traces to 

1. logs

  Intro: print statements don't scale. We need to think about how MULTIPLE
  instances of our application will be generating logs. And we need to make them
  searchable, especially days/weeks after they were created.

  - log levels (in our appliation, where are the different levels appropriate)
  - control log level with environment variable
  - organize logger in code, e.g. have a log_config.py file that inits the logger
    and then show how to import and use it in all of the other files

    - put log statements in 
        - middlewares and api route handler
        - in the routes themselves
        - in helper functions that the routes call (potentially, or warn against this)

  - how to get logs to cloudwatch
  - cloudwatch logs concepts: log groups, log streams, log events
    - how billing works for these
    - how they are meant to be used

  - CORRELATION: how do you find relevant logs created from
    - API GW
    - lambda
    - "single pane of glass"
    
  - workflow for using logs (quote Alex DeBrie "what do you do with your logs" "we store them")
    - query logs with logs insights QL (talk about cost, e.g. scanning)
    - live tail (there is some free live tail time on the free tier)
    - uses
        - find errors--logs are where you find root cause, e.g. traceback
        - find performance issues (latency)
        - metrics

  - structured logs

2. metrics / alarms / dashboards
  - 

3. traces
  - correlating logs across services
  - understanding which services a transaction goes through (a subset, or in which order)
  - profiling, where are latency bottlenecks in the distributed system
  - 

4. dashboards
  - super dashboard
    - node graph
    - convenience URLs (in the markdown)
      - xray and the relevant traces
      - cloudwatch logs insights
      - relevant cloudwatch log groups and streams
      - resources
        - s3
        - api gateway
        - lambda
  - parameterized dashboard

5. alerts

6. workflow for monitoring to use all of the above


"""

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
from aws_xray_sdk.core.models.segment import Segment
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)

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
