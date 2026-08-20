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
        self.public_s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_PUBLIC_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def generate_presigned_upload_url(self, user_id, filename):
        """Generate a presigned URL for uploading a file to S3."""
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_key = f"user_{user_id}/{unique_name}"

        upload_url = self.public_s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket_name, "Key": file_key},
            ExpiresIn=900,
        )

        return file_key, upload_url

    def generate_presigned_download_url(self, file_key, filename):
        """Generate a presigned URL for downloading a file from S3."""
        params = {
            "Bucket": self.bucket_name,
            "Key": file_key,
        }

        if filename:
            params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'

        download_url = self.public_s3_client.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=900,
        )

        return download_url

    def delete_file(self, file_key):
        """Delete a file from S3 using the provided file key."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
        except ClientError as e:
            raise e


s3_service = S3Service()
