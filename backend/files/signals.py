import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import File
from .services import s3_service

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=File)
def delete_file_from_s3(sender, instance, **kwargs):
    if instance.file_key:
        try:
            s3_service.delete_file(instance.file_key)
            logger.info(f"Deleted file from S3: {instance.file_key}")
        except Exception as e:
            logger.error(
                f"Error deleting file from S3: {instance.file_key}. Error: {str(e)}"
            )
