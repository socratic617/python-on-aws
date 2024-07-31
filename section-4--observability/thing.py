import httpx

from aws_xray_sdk.core import (
    patch_all,
    xray_recorder,
)

# Patch all libraries to be instrumented by AWS X-Ray
# patch_all()

sampling_rules = {
    "version": 1,  # Ensure the version field is set correctly
    "rules": [
        # {
        #     "RuleName": "DefaultRule",
        #     "Priority": 1,
        #     "FixedRate": 1.0,
        #     "ReservoirSize": 100,
        #     "ServiceName": "*",
        #     "ServiceType": "*",
        #     "HTTPMethod": "*",
        #     "URLPath": "*",
        #     "Host": "*",
        #     "ResourceARN": "*",
        #     "Version": 1,
        # },
    ],
    "default": {
        "FixedRate": 0.1,
        "ReservoirSize": 1,
        "FixedTarget": 1,
        "fixed_target": 1,
        "rate": 0.1,
        "Rate": 0.1,
    },
}

# trace config
xray_recorder.configure(
    service="my-service",
    daemon_address="localhost:2000",
    sampling=True,
    sampling_rules=sampling_rules,
)

