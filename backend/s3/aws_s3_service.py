import os
import boto3
from botocore.client import Config
from functools import lru_cache
from fastapi import Depends
from typing import Annotated

S3_LOCAL_ENDPOINT_URL = os.environ["S3_LOCAL_ENDPOINT_URL"]
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = os.environ["AWS_REGION"]
ENVIRONMENT = os.environ["ENVIRONMENT"]


@lru_cache()
def get_s3_client():
    if ENVIRONMENT == "development":
        return boto3.client(
            "s3",
            endpoint_url=S3_LOCAL_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name=AWS_REGION,
            verify=False,
        )
    elif ENVIRONMENT == "production":
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
    else:
        raise Exception()


async def get_s3():
    client = get_s3_client()
    try:
        yield client
    finally:
        # Cleanup if needed
        pass


AwsS3ClientDependency = Annotated[boto3.client, Depends(get_s3)]
