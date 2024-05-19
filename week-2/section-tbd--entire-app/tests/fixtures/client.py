from typing import Generator

import pytest
from fastapi.testclient import TestClient
from files_api.main import create_app
from files_api.settings import Settings
from mypy_boto3_s3 import S3Client
from tests.consts import TEST_BUCKET_NAME


# pylint: disable=unused-argument
@pytest.fixture
def client(s3_client: S3Client) -> Generator[TestClient, None, None]:
    settings = Settings(s3_bucket_name=TEST_BUCKET_NAME)
    app = create_app(settings)

    # using a context manager activates the lifespan method
    with TestClient(app) as client:
        yield client
