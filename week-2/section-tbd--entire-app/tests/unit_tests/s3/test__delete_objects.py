
from files_api.s3.delete_objects import delete_s3_object
from mypy_boto3_s3 import S3Client

BUCKET_NAME = "test-bucket"


def test_delete_existing_s3_object(s3_client: S3Client):
    s3_client.put_object(Bucket=BUCKET_NAME, Key="testfile.txt", Body="test content")
    assert delete_s3_object(BUCKET_NAME, "testfile.txt") is True
    assert not s3_client.list_objects_v2(Bucket=BUCKET_NAME).get("Contents")


# pylint: disable=unused-argument
def test_delete_nonexistent_s3_object(s3_client: S3Client):
    delete_s3_object(BUCKET_NAME, "nonexistent.txt")
    assert delete_s3_object(BUCKET_NAME, "nonexistent.txt") is False
