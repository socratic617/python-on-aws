# In src/files_api/s3/write_objects.py
from typing import Optional

import boto3

try:
    from mypy_boto3_s3 import S3Client
except ImportError:
    ...


def upload_s3_object(
    bucket_name: str,
    object_key: str,
    file_content: bytes,
    s3_client: Optional["S3Client"] = None,
) -> None:
    s3_client = s3_client or boto3.client("s3")
    s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=file_content)
