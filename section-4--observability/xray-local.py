import os

os.environ["AWS_XRAY_TRACING_NAME"] = "xray-playground"
AWS_PROFILE = "cloud-course"
SEND_TRACES_TO_XRAY = True

os.environ["AWS_PROFILE"] = AWS_PROFILE
os.environ["AWS_REGION"] = "us-west-2"


from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.emitters.udp_emitter import UDPEmitter
from aws_xray_sdk.core.models.segment import Segment
import boto3
from rich import print

# Set up X-Ray recorder
# xray_recorder.configure()

class DirectXrayEmitter:
    def __init__(self):
        self.client = boto3.client('xray')

    def send_entity(self, entity):
        serialized_entity = entity.serialize()
        self.client.put_trace_segments(
            TraceSegmentDocuments=[serialized_entity]
        )
        print(serialized_entity)

# Use the custom emitter
xray_recorder.emitter = DirectXrayEmitter()


# Example of creating a segment
segment = xray_recorder.begin_segment('my-test-segment')
# Add annotations or metadata to the segment if needed
segment.put_annotation('key', 'value')

# End the segment
xray_recorder.end_segment()
