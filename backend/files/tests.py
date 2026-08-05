from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from files.models import File

User = get_user_model()


class FileAPITestCase(APITestCase):
    """Test suite for the File API endpoints."""

    def setUp(self):
        """Set up test users and URLs for file API tests."""
        self.user_a = User.objects.create_user(
            email="user_a@example.com", password="password123"
        )
        self.user_b = User.objects.create_user(
            email="user_b@example.com", password="password123"
        )

        self.list_url = reverse("file-list")

        self.client.force_authenticate(user=self.user_a)

    def test_upload_file_success(self):
        """Test successful file upload."""
        file_content = b"Test binary content for file"
        uploaded_file = SimpleUploadedFile(
            "file.pdf", file_content, content_type="application/pdf"
        )

        body = {"uploaded_file": uploaded_file}
        response = self.client.post(self.list_url, body, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        db_file = File.objects.first()
        self.assertEqual(bytes(db_file.file), file_content)

    def test_upload_string_instead_of_file(self):
        """Test uploading a string instead of a file."""
        body = {"uploaded_file": "just a regular string, not a file"}
        response = self.client.post(self.list_url, body, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(File.objects.count(), 0)

    def test_get_queryset_user_isolation(self):
        """Test that users can only see their own files."""
        File.objects.create(user=self.user_a, file=b"data1", name="file_a.txt", size=5)
        File.objects.create(user=self.user_b, file=b"data2", name="file_b.txt", size=5)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "file_a.txt")

    def test_rename_file_success(self):
        """Test successful renaming of a file."""
        file_obj = File.objects.create(
            user=self.user_a,
            file=b"important bytes",
            name="old_name.txt",
            size=15,
        )

        body = {"name": "new_name.txt"}
        detail_url = reverse("file-detail", kwargs={"pk": file_obj.pk})
        response = self.client.patch(detail_url, body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file_obj.refresh_from_db()
        self.assertEqual(file_obj.name, "new_name.txt")

    def test_update_restricted_fields(self):
        """Test that restricted fields cannot be updated."""
        file_obj = File.objects.create(
            user=self.user_a,
            file=b"original content",
            name="document.pdf",
            size=100,
        )

        detail_url = reverse("file-detail", kwargs={"pk": file_obj.pk})
        body = {"size": 999999, "uploaded_file": "just a string"}
        response = self.client.patch(detail_url, body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file_obj.refresh_from_db()
        self.assertEqual(file_obj.size, 100)
        self.assertEqual(bytes(file_obj.file), b"original content")
