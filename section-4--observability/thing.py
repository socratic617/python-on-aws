import httpx

from aws_xray_sdk.core import (
    patch_all,
    xray_recorder,
)
from aws_xray_sdk.core.models.segment import Segment
from rich import inspect
from rich.console import Console



sampling_rules = {
  "version": 2,
  "rules": [
    {
      "description": "Match all traces",
      "host": "*",
      "http_method": "*",
      "url_path": "*",
      "fixed_target": 1,
      "rate": 1.0
    }
  ],
  "default": {
    "fixed_target": 1,
    "rate": 1.0
  }
}


# Patch all libraries to be instrumented by AWS X-Ray
patch_all()

# trace config
xray_recorder.configure(
    service="my-service",
    daemon_address="localhost:2000",
    # sampling=True,
    # sampling_rules=sampling_rules,
)


console = Console(force_terminal=True)

with xray_recorder.in_segment("test-segment") as segment:
    segment: Segment
    segment.put_annotation("name", "Eric")
    inspect(xray_recorder.current_segment(), console=console)

    with xray_recorder.in_subsegment("test-subsegment") as subsegment:
        subsegment.put_annotation("name", "Eric Sub")
        inspect(xray_recorder.current_subsegment(), console=console)

        from time import sleep
        sleep(0.5)
