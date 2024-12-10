import uuid
from fastapi import APIRouter, HTTPException, UploadFile
from backend.s3.aws_s3_service import (
    init_s3_client,
)
from backend.s3.s3_constants import BUCKET_NAME, PRESIGNED_URL_EXPIRATION
from backend.file.file_model import Profile, File
from backend.database.database import DatabaseDependency
from backend.user.user_authentication import UserAuthenticationContextDependency
from backend.user.user_models import User

router = APIRouter()

s3 = init_s3_client()


@router.post("/users/profiles/create")
async def create_profile(
    file: UploadFile,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):

    if not file.filename or not file.content_type:
        raise HTTPException(400, "File must have both name and content type")

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except:
        s3.create_bucket(Bucket=BUCKET_NAME)
    clean_filename = file.filename.replace(" ", "_")
    file_key = f"profiles/{user.id}/{uuid.uuid4()}-{clean_filename}"
    file_content = await file.read()

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Body=file_content,
        ContentType=file.content_type,
        ACL="private",
    )

    # Generate a pre-signed URL for immediate viewing
    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": file_key},
        ExpiresIn=PRESIGNED_URL_EXPIRATION,
    )

    # Deactivate existing profiles
    existing_profiles = (
        db.query(Profile)
        .filter(Profile.user_id == user.id, Profile.is_active == True)
        .all()
    )

    for profile in existing_profiles:
        profile.is_active = False

    # Store the file_key instead of the full URL
    new_file = File(
        name=file.filename,
        file_type=file.content_type,
        size=len(file_content),
        path=file_key,  # Store just the key
        user_id=user.id,
    )
    db.add(new_file)
    db.flush()

    profile = Profile(file_id=new_file.id, user_id=user.id)
    db.add(profile)
    db.commit()

    return {"message": "Profile created successfully", "file_url": presigned_url}


@router.get("/users/profiles/upload-url")
async def get_upload_url(
    filename: str,
    content_type: str,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    if not filename or not content_type:
        raise HTTPException(400, "Filename and content type are required")

    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Generate unique file key
    file_key = f"profiles/{user.id}/{uuid.uuid4()}-{filename}"

    # Generate presigned POST URL
    presigned_post = s3.generate_presigned_post(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Fields={
            "Content-Type": content_type,
        },
        Conditions=[
            {"Content-Type": content_type},
            ["content-length-range", 1, 10485760],  # 10MB max size
        ],
        ExpiresIn=3600,
    )

    return {"presigned_post": presigned_post, "file_key": file_key}


@router.post("/users/profiles/complete-upload")
async def complete_profile_upload(
    file_key: str,
    filename: str,
    content_type: str,
    file_size: int,
    db: DatabaseDependency,
    auth_context: UserAuthenticationContextDependency,
):
    user = db.query(User).filter(User.id == auth_context.user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Deactivate existing profiles
    existing_profiles = (
        db.query(Profile)
        .filter(Profile.user_id == user.id, Profile.is_active == True)
        .all()
    )

    for profile in existing_profiles:
        profile.is_active = False

    new_file = File(
        name=filename,
        file_type=content_type,
        size=file_size,
        path=file_key,
        user_id=user.id,
    )
    db.add(new_file)
    db.flush()

    profile = Profile(file_id=new_file.id, user_id=user.id)
    db.add(profile)
    db.commit()

    # Generate a presigned URL for viewing
    presigned_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET_NAME, "Key": file_key}, ExpiresIn=3600
    )

    return {"message": "Profile created successfully", "file_url": presigned_url}
