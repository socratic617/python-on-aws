"""Test cases for `s3.write_objects`."""

from files_api.s3.write_objects import upload_s3_object
from mypy_boto3_s3 import S3Client
from tests.consts import TEST_BUCKET_NAME


def test_upload_s3_object(s3_client: S3Client): ...
