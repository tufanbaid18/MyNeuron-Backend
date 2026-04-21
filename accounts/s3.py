import boto3
from django.conf import settings

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

def presigned_url(key, expires=None):
    if not key:
        return None

    expires = expires or int(
        settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
    )

    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": key,
        },
        ExpiresIn=expires,
    )


import uuid

def generate_upload_url(file_name, content_type="image/jpeg", folder="articles/temp"):
    ext = file_name.split(".")[-1]
    key = f"{folder}/{uuid.uuid4()}.{ext}"

    upload_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=300,
    )

    return key, upload_url

def move_s3_file(old_key, new_key):
    if not old_key:
        return new_key

    # Only move temp files
    if not old_key.startswith("articles/temp/"):
        return old_key

    bucket = settings.AWS_STORAGE_BUCKET_NAME

    # Copy
    s3.copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": old_key},
        Key=new_key,
    )

    # Delete old temp file
    s3.delete_object(Bucket=bucket, Key=old_key)

    return new_key


def upload_file_to_s3(file, folder="articles/temp"):
    import uuid

    ext = file.name.split(".")[-1]
    key = f"{folder}/{uuid.uuid4()}.{ext}"

    s3.upload_fileobj(
        file,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    return key