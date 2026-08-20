from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import FormParser, MultiPartParser
from .serializers import FileSerializer, FileUpdateSerializer
from .services import s3_service
from .models import File


class FileViewSet(ModelViewSet):
    """ViewSet for managing file uploads, updates, and deletions."""

    def get_queryset(self):
        """Return the queryset of files belonging to the authenticated user."""
        user = self.request.user

        return File.objects.filter(user=user)

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action."""
        if self.action in ["update", "partial_update"]:
            return FileUpdateSerializer
        return FileSerializer

    def perform_create(self, serializer):
        """Save file metadata to DB and generate a presigned URL for direct S3 upload."""
        filename = serializer.validated_data["name"]

        file_key, presigned_url = s3_service.generate_presigned_url(
            self.request.user.id, filename
        )

        instance = serializer.save(
            user=self.request.user,
            file_key=file_key,
        )

        instance.presigned_url = presigned_url
