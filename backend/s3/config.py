# s3 cors
def get_cors_configuration(allowed_origins: str):

    return {
        "CORSRules": [
            {
                "AllowedHeaders": [
                    "Authorization",
                    "Content-Type",
                    "x-amz-date",
                    "x-amz-content-sha256",
                    "x-amz-security-token",
                ],
                "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
                "AllowedOrigins": allowed_origins,
                "ExposeHeaders": ["ETag"],
                "MaxAgeSeconds": 3000,
            }
        ]
    }


# s3 encryption
def get_encryption_configuration():
    return {
        "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
    }


# lifecycle
def get_lifecycle_configuration(nonactive_days: int = 90, multipart_days: int = 7):
    return {
        "Rules": [
            {
                "ID": "DeleteOldFiles",
                "Status": "Enabled",
                "ExpiredObjectDeleteMarker": True,
                "NoncurrentVersionExpiration": {"NoncurrentDays": nonactive_days},
                "AbortIncompleteMultipartUpload": {
                    "DaysAfterInitiation": multipart_days
                },
            }
        ]
    }


# s3 bucket_policy
def get_bucket_policy(bucket_name: str, account_id: str):
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DenyNonSSLRequests",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*",
                ],
                "Condition": {"Bool": {"aws:SecureTransport": "false"}},
            },
            {
                "Sid": "DenyUnencryptedObjectUploads",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "StringNotEquals": {"s3:x-amz-server-side-encryption": "AES256"}
                },
            },
            {
                "Sid": "AllowPresignedUrlAccess",
                "Effect": "Allow",
                "Principal": {"AWS": f"arn:aws:iam::{account_id}:root"},
                "Action": ["s3:GetObject", "s3:PutObject"],
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            },
        ],
    }


# s3 public_access
def get_public_access_configuration():
    return {
        "BlockPublicAcls": True,
        "IgnorePublicAcls": True,
        "BlockPublicPolicy": True,
        "RestrictPublicBuckets": True,
    }
