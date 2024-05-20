from fastapi import status
from fastapi.testclient import TestClient
from mypy_boto3_s3 import S3Client
from tests.consts import TEST_BUCKET_NAME


def test_upload_file(client: TestClient):
    file_content = b"test content"
    files = {"file": ("testfile.txt", file_content, "text/plain")}

    response = client.post("/files/testfile.txt", files=files)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "File uploaded: testfile.txt"}

    response = client.get("/files/testfile.txt")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == file_content


def test_overwrite_file(client: TestClient, s3_client: S3Client):
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="testfile.txt", Body="old content")

    file_content = b"new content"
    files = {"file": ("testfile.txt", file_content, "text/plain")}

    response = client.post("/files/testfile.txt", files=files)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "File overwritten: testfile.txt"}

    response = client.get("/files/testfile.txt")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == file_content
