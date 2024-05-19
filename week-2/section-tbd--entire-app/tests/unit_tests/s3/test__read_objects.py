
from files_api.s3.read_objects import (
    fetch_s3_objects,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from files_api.s3.write_objects import upload_s3_object
from mypy_boto3_s3 import S3Client

BUCKET_NAME = "test-bucket"


def test_upload_s3_object(s3_client: S3Client):
    file_content = b"test content"
    upload_s3_object(BUCKET_NAME, "testfile.txt", file_content)
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key="testfile.txt")
    assert response["Body"].read() == file_content


def test_object_exists_in_s3(s3_client: S3Client):
    s3_client.put_object(Bucket=BUCKET_NAME, Key="testfile.txt", Body="test content")
    assert object_exists_in_s3(BUCKET_NAME, "testfile.txt") is True
    assert object_exists_in_s3(BUCKET_NAME, "nonexistent.txt") is False


def test_pagination(s3_client: S3Client):
    # Upload 5 objects
    for i in range(1, 6):
        s3_client.put_object(Bucket=BUCKET_NAME, Key=f"file{i}.txt", Body=f"content {i}")

    # Paginate 2 at a time
    files, next_page_token = fetch_s3_objects(BUCKET_NAME, max_keys=2)
    assert len(files) == 2
    assert files[0]["Key"] == "file1.txt"
    assert files[1]["Key"] == "file2.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(BUCKET_NAME, next_page_token, max_keys=2)
    assert len(files) == 2
    assert files[0]["Key"] == "file3.txt"
    assert files[1]["Key"] == "file4.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(BUCKET_NAME, next_page_token, max_keys=2)
    assert len(files) == 1
    assert files[0]["Key"] == "file5.txt"
    assert next_page_token is None


def test_mixed_page_sizes(s3_client: S3Client):
    # Upload 5 objects
    for i in range(1, 6):
        s3_client.put_object(Bucket=BUCKET_NAME, Key=f"file{i}.txt", Body=f"content {i}")

    # Paginate with mixed page sizes
    files, next_page_token = fetch_s3_objects(BUCKET_NAME, max_keys=3)
    assert len(files) == 3
    assert files[0]["Key"] == "file1.txt"
    assert files[1]["Key"] == "file2.txt"
    assert files[2]["Key"] == "file3.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(BUCKET_NAME, next_page_token, max_keys=1)
    assert len(files) == 1
    assert files[0]["Key"] == "file4.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(BUCKET_NAME, next_page_token, max_keys=2)
    assert len(files) == 1
    assert files[0]["Key"] == "file5.txt"
    assert next_page_token is None


def test_directory_queries(s3_client: S3Client):
    # Upload nested objects
    s3_client.put_object(Bucket=BUCKET_NAME, Key="folder1/file1.txt", Body="content 1")
    s3_client.put_object(Bucket=BUCKET_NAME, Key="folder1/file2.txt", Body="content 2")
    s3_client.put_object(Bucket=BUCKET_NAME, Key="folder2/file3.txt", Body="content 3")
    s3_client.put_object(Bucket=BUCKET_NAME, Key="folder2/subfolder1/file4.txt", Body="content 4")
    s3_client.put_object(Bucket=BUCKET_NAME, Key="file5.txt", Body="content 5")

    # Query with prefix
    files, next_page_token = fetch_s3_objects(BUCKET_NAME, prefix="folder1/")
    assert len(files) == 2
    assert files[0]["Key"] == "folder1/file1.txt"
    assert files[1]["Key"] == "folder1/file2.txt"
    assert next_page_token is None

    # Query with prefix for nested folder
    files, next_page_token = fetch_s3_objects(BUCKET_NAME, prefix="folder2/subfolder1/")
    assert len(files) == 1
    assert files[0]["Key"] == "folder2/subfolder1/file4.txt"
    assert next_page_token is None

    # Query with no prefix
    files, next_page_token = fetch_s3_objects(BUCKET_NAME)
    assert len(files) == 5
    assert files[0]["Key"] == "file5.txt"
    assert files[1]["Key"] == "folder1/file1.txt"
    assert files[2]["Key"] == "folder1/file2.txt"
    assert files[3]["Key"] == "folder2/file3.txt"
    assert files[4]["Key"] == "folder2/subfolder1/file4.txt"
    assert next_page_token is None
