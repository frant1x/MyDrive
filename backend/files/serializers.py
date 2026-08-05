from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    uploaded_file = serializers.FileField(write_only=True)

    class Meta:
        model = File
        fields = ["id", "uploaded_file", "user", "name", "size", "created_at"]
        read_only_fields = ["id", "user", "name", "size", "created_at"]

    def create(self, validated_data):
        uploaded_file = validated_data.pop("uploaded_file")

        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name
        file_size = uploaded_file.size

        user = validated_data.pop("user")

        return File.objects.create(
            file=file_bytes, user=user, name=file_name, size=file_size
        )


class FileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["name"]
