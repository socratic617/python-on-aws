"""Example pytest fixture."""

import os
from typing import Generator

import boto3
import pytest
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from tests.consts import TEST_BUCKET_NAME


def point_away_from_aws():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def s3_client() -> Generator[S3Client, None, None]:
    with mock_aws():
        point_away_from_aws()

        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

        yield s3_client

        # delete the bucket and its objects
        objects = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME).get("Contents", [])
        if objects:
            s3_client.delete_objects(
                Bucket=TEST_BUCKET_NAME, Delete={"Objects": [{"Key": obj["Key"]} for obj in objects]}
            )
        s3_client.delete_bucket(Bucket=TEST_BUCKET_NAME)
