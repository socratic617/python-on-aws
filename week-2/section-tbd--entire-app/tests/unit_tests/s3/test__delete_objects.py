"""Test cases for `s3.delete_objects`."""

from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import object_exists_in_s3
from files_api.s3.write_objects import upload_s3_object
from mypy_boto3_s3 import S3Client
from tests.consts import TEST_BUCKET_NAME


def test_delete_existing_s3_object(s3_client: S3Client):
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="testfile.txt", Body="test content")
    delete_s3_object(TEST_BUCKET_NAME, "testfile.txt")
    assert not s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME).get("Contents")


# pylint: disable=unused-argument
def test_delete_nonexistent_s3_object(s3_client: S3Client):
    # create a file
    upload_s3_object(TEST_BUCKET_NAME, "testfile.txt", b"test content")
    # delete the file, so we know it is not present
    delete_s3_object(TEST_BUCKET_NAME, "testfile.txt")
    # delete it again... nothing should happen
    delete_s3_object(TEST_BUCKET_NAME, "testfile.txt")
    # the file should still not be present
    assert object_exists_in_s3(TEST_BUCKET_NAME, "testfile.txt") is False
