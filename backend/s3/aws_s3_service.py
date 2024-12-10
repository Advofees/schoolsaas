import json
import boto3
from botocore.client import Config
from backend.s3.config import (
    get_cors_configuration,
    get_encryption_configuration,
    get_lifecycle_configuration,
    get_bucket_policy,
    get_public_access_configuration,
)
from backend.s3.s3_constants import (
    ENVIRONMENT,
    S3_LOCAL_ENDPOINT_URL,
    AWS_SECRET_ACCESS_KEY,
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    BUCKET_NAME,
)


def init_s3_client():
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
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        )
    else:
        raise Exception()


def ensure_bucket_exists(bucket_name: str, region: str, account_id: str):
    s3_client = init_s3_client()
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except:
        if region == AWS_REGION:
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )

    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration=get_public_access_configuration(),
    )

    s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration=get_encryption_configuration(),
    )

    s3_client.put_bucket_cors(
        Bucket=bucket_name,
        CORSConfiguration=get_cors_configuration(allowed_origins="*"),
    )

    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(get_bucket_policy(bucket_name, account_id)),
    )

    s3_client.put_bucket_lifecycle_configuration(
        Bucket=bucket_name, LifecycleConfiguration=get_lifecycle_configuration()
    )


def get_account_id():
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Account"]


def verify_bucket_configuration():
    s3 = init_s3_client()
    # Check encryption
    encryption = s3.get_bucket_encryption(Bucket=BUCKET_NAME)
    print("Encryption configured:", encryption)

    # Check public access block
    public_access = s3.get_public_access_block(Bucket=BUCKET_NAME)
    print("Public access block configured:", public_access)

    # Check CORS
    cors = s3.get_bucket_cors(Bucket=BUCKET_NAME)
    print("CORS configured:", cors)

    # Check bucket policy
    policy = s3.get_bucket_policy(Bucket=BUCKET_NAME)
    print("Bucket policy configured:", policy)

    return True


# Call these when your app starts

# ensure_bucket_exists(
#     bucket_name=BUCKET_NAME, region=AWS_REGION, account_id=get_account_id()
# )
# verify_bucket_configuration()
