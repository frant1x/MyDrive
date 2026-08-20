from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
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


class FileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating the File model, allowing only the name to be updated."""

    class Meta:
        model = File
        fields = ["name"]
