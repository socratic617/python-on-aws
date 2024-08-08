from fastapi import FastAPI
import aws_xray_sdk
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Initialize X-Ray
xray_recorder.configure(
    service="fastapi-xray-service",
    sampling_rules={
        "version": 2,
        "rules": [],
        "default": {"fixed_target": 1, "rate": 1.0},
    },
    sampling=True,
)
patch_all()

app = FastAPI()


@app.get("/")
def read_root():
    with xray_recorder.in_segment("root_segment") as segment:
        segment.put_annotation("example", "annotation")
        return {"message": "Hello, X-Ray!"}
