from fastapi import status
from fastapi.testclient import TestClient
from mypy_boto3_s3 import S3Client
from tests.consts import TEST_BUCKET_NAME


def test_list_files_empty(client: TestClient):
    response = client.get("/files/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"files": [], "next_page_token": None}


def test_list_files_with_objects(client: TestClient, s3_client: S3Client):  # noqa: R701
    for i in [1, 2, 3, 4, 5]:
        s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key=f"file{i}.txt", Body=f"content {i}")

    response = client.get("/files/?page_size=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["files"]) == 2
    assert data["next_page_token"]

    response = client.get(f"/files/?page_size=2&page_token={data['next_page_token']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["files"]) == 2
    assert data["next_page_token"]

    response = client.get(f"/files/?page_size=2&page_token={data['next_page_token']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["files"]) == 1
    assert data["next_page_token"] is None
