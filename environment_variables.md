# Variables
`create .env and add the following`

## security
SECRET_STRING="secret-string"
JWT_SECRET_KEY=jwt-secret-key

## Database
DATABASE_HOST="127.0.0.1"
DATABASE_NAME="postgres"
DATABASE_USER="postgres"
DATABASE_PASSWORD="postgres"

## MinIO Configuration(local s3)
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=main

## local Mail server

MAIL_SERVER_HOST="localhost"
MAIL_SERVER_PORT="1025"
MAIL_SERVER_USERNAME=""
MAIL_SERVER_PASSWORD=""
MAIL_USE_TLS=False
MAIL_USE_SSL=False
