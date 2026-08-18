import uuid
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


class S3Service:
    """Service class for handling S3 operations."""

    def __init__(self):
        """Initialize the S3 client with the provided settings."""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def upload_file(self, file_obj, user_id):
        """Upload a file to S3 and return the generated file key."""
        unique_name = f"{uuid.uuid4()}_{file_obj.name}"
        file_key = f"user_{user_id}/{unique_name}"

        self.s3_client.upload_fileobj(
            file_obj,
            self.bucket_name,
            file_key,
            ExtraArgs={"ContentType": file_obj.content_type},
        )

        return file_key

    def delete_file(self, file_key: str):
        """Delete a file from S3 using the provided file key."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
        except ClientError as e:
            raise e


s3_service = S3Service()
