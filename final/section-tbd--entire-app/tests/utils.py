import boto3
import botocore


def delete_s3_bucket(bucket_name: str):
    """Delete an S3 bucket and all its contents."""
    s3_client = boto3.client("s3")

    try:
        # Delete all objects in the bucket
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        if "Contents" in objects:
            for obj in objects["Contents"]:
                s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
        # Delete the bucket itself
        s3_client.delete_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError:
        pass
