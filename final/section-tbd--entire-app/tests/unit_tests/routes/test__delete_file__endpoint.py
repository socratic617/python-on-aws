from fastapi import status
from fastapi.testclient import TestClient
from mypy_boto3_s3 import S3Client
from tests.consts import TEST_BUCKET_NAME


def test_delete_file_not_found(client: TestClient):
    response = client.delete("/files/nonexistent.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "File not found: nonexistent.txt"}


def test_delete_file(client: TestClient, s3_client: S3Client):
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="testfile.txt", Body="test content")

    response = client.delete("/files/testfile.txt")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Deleted file: testfile.txt"}

    response = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME)
    assert "Contents" not in response
