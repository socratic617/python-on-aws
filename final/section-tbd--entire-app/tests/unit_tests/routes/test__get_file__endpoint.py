from fastapi import status
from fastapi.testclient import TestClient
from mypy_boto3_s3 import S3Client
from tests.consts import TEST_BUCKET_NAME


def test_get_file_not_found(client: TestClient):
    response = client.get("/files/nonexistent.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "File not found: nonexistent.txt"}


def test_get_file(client: TestClient, s3_client: S3Client):
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="testfile.txt", Body="test content")

    response = client.get("/files/testfile.txt")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"test content"
