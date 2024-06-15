from fastapi import status
from fastapi.testclient import TestClient
from tests.consts import TEST_BUCKET_NAME
from tests.utils import delete_s3_bucket


def test_get_nonexistent_file(client: TestClient):
    response = client.get("/files/nonexistent_file.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "File not found"}


def test_head_nonexistent_file(client: TestClient):
    response = client.head("/files/nonexistent_file.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_file(client: TestClient):
    response = client.delete("/files/nonexistent_file.txt")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "File not found"}


def test_internal_server_error(client: TestClient):
    # Delete the test bucket to trigger an internal server error
    delete_s3_bucket(bucket_name=TEST_BUCKET_NAME)

    # Attempt to describe files, this should fail because the bucket does not exist
    # It is unfortunate that this test relies on knowing the implementation of the endpoint,
    # but if an API is designed well, clients should NEVER be able to elicit a 500 server error.
    # 500 errors generally should only be caused by bugs in the server implementation.
    response = client.get("/files")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "message" in response.json()
    assert response.json()["message"] == "An unexpected error occurred."


def test_validation_mutually_exclusive_parameters(client: TestClient):
    # Sending both page_token and directory should raise a 422 error
    response = client.get("/files?page_size=10&page_token=some_token&directory=not_default")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "errors" in response.json()
    assert response.json()["errors"] == [
        "Value error, When page_token is provided, page_size and directory must not be set."
    ]


def test_validation_page_size_greater_than_one(client: TestClient):
    """Sending page_size less than or equal to 0 should raise a 422 error."""
    response = client.get("/files?page_size=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert "detail" in response.json()
    assert "page_size" in str(response.json()["detail"])

    response = client.get("/files?page_size=-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()
    assert "page_size" in str(response.json()["detail"])
