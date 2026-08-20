from rest_framework import serializers
from .models import File
import os


class BaseFileSerializer(serializers.ModelSerializer):
    """Base serializer for the File model, providing common fields and validation."""

    def _get_unique_name(self, user, name):
        """Generate a unique file name for the given user and name."""
        name, extension = os.path.splitext(name)
        counter = 1
        unique_name = name

        queryset = File.objects.filter(user=user)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        while queryset.filter(user=user, name=unique_name + extension).exists():
            unique_name = f"{name} ({counter})"
            counter += 1

        return unique_name + extension

    def validate_name(self, value):
        """Validate the file name to ensure it is unique for the user."""
        user = self.context["request"].user
        return self._get_unique_name(user, value)


class FileSerializer(BaseFileSerializer):
    """Serializer for the File model, providing file metadata and presigned upload URL."""

    presigned_upload_url = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = [
            "id",
            "presigned_upload_url",
            "file_key",
            "user",
            "name",
            "size",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "file_key",
            "presigned_upload_url",
        ]


class FileUpdateSerializer(BaseFileSerializer):
    """Serializer for updating the File model, allowing only the name to be updated."""

    class Meta:
        model = File
        fields = ["name"]
