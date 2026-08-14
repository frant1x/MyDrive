from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
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
        validated_data.pop("uploaded_file", None)

        return super().create(validated_data)


class FileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["name"]
