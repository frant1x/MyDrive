from django.db import models
from authentication.models import User


class File(models.Model):
    """Model representing a file uploaded by a user."""

    file_key = models.CharField(max_length=512, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="files")
    name = models.CharField(max_length=255, unique=True)
    size = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
