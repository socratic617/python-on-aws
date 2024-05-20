"""Example pytest fixture."""

import os
from typing import Generator

import boto3
import pytest
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
    """
    Yield a mocked S3 client to be used in tests.

    Set up a bucket for testing as well, under the name `TEST_BUCKET_NAME`.
    """
    point_away_from_aws()
    # ...
    yield
