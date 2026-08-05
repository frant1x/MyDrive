from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import FormParser, MultiPartParser
from .serializers import FileSerializer, FileUpdateSerializer
from .models import File


class FileViewSet(ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        return File.objects.filter(user=user).defer("file")

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return FileUpdateSerializer
        return FileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
