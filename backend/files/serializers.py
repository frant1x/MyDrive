from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    """Serializer for the File model, handling file uploads and metadata."""

    uploaded_file = serializers.FileField(write_only=True)

    class Meta:
        model = File
        fields = [
            "id",
            "uploaded_file",
            "file_key",
            "user",
            "name",
            "size",
            "created_at",
        ]
        read_only_fields = ["id", "user", "name", "size", "created_at", "file_key"]

    def create(self, validated_data):
        """Override the create method to handle file upload and metadata extraction."""
        validated_data.pop("uploaded_file", None)

        return super().create(validated_data)


class FileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating the File model, allowing only the name to be updated."""

    class Meta:
        model = File
        fields = ["name"]
