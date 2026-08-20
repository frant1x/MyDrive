from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
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

        file_key, presigned_upload_url = s3_service.generate_presigned_upload_url(
            self.request.user.id, filename
        )

        instance = serializer.save(
            user=self.request.user,
            file_key=file_key,
        )

        instance.presigned_upload_url = presigned_upload_url

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        presigned_download_url = s3_service.generate_presigned_download_url(
            file_obj.file_key, file_obj.name
        )

        return Response({"presigned_download_url": presigned_download_url})
