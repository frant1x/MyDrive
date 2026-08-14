from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import FormParser, MultiPartParser
from .serializers import FileSerializer, FileUpdateSerializer
from .services import s3_service
from .models import File


class FileViewSet(ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        return File.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return FileUpdateSerializer
        return FileSerializer

    def perform_create(self, serializer):
        uploaded_file = serializer.validated_data["uploaded_file"]

        file_key = s3_service.upload_file(uploaded_file, self.request.user.id)

        serializer.save(
            user=self.request.user,
            file_key=file_key,
            name=uploaded_file.name,
            size=uploaded_file.size,
        )
