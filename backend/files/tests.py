from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from files.models import File
from unittest.mock import patch

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

    @patch("files.views.s3_service.generate_presigned_upload_url")
    def test_create_file_generates_presigned_url(self, mock_generate_url):
        """Test creating a file record and receiving a presigned upload URL."""
        mock_file_key = f"user_{self.user_a.id}/fake-uuid_document.pdf"
        mock_upload_url = "http://localhost:9000/my-app-files/presigned-url"
        mock_generate_url.return_value = (mock_file_key, mock_upload_url)

        body = {
            "name": "document.pdf",
            "size": 1024,
        }
        response = self.client.post(self.list_url, body, format="json")

        self.assertEqual(response.data["presigned_upload_url"], mock_upload_url)
        self.assertEqual(response.data["file_key"], mock_file_key)

        mock_generate_url.assert_called_once_with(self.user_a.id, "document.pdf")

        db_file = File.objects.first()
        self.assertIsNotNone(db_file)
        self.assertEqual(db_file.file_key, mock_file_key)

    def test_create_file_missing_required_fields(self):
        """Test that creating a file without name or size fails."""
        response = self.client.post(self.list_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("size", response.data)
        self.assertEqual(File.objects.count(), 0)

    def test_get_queryset_user_isolation(self):
        """Test that users can only see their own files."""
        File.objects.create(
            user=self.user_a, file_key="user_a/file1.txt", name="file_a.txt", size=5
        )
        File.objects.create(
            user=self.user_b, file_key="user_b/file2.txt", name="file_b.txt", size=5
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "file_a.txt")

    @patch("files.views.s3_service.generate_presigned_download_url")
    def test_download_file_success(self, mock_generate_download_url):
        """Test generating a presigned download URL for an existing user file."""
        file_obj = File.objects.create(
            user=self.user_a,
            file_key="user_a/test_download.pdf",
            name="invoice.pdf",
            size=2048,
        )
        mock_download_url = (
            "http://localhost:9000/my-app-files/user_a/test_download.pdf?token=abc"
        )
        mock_generate_download_url.return_value = mock_download_url

        download_url = reverse("file-download", kwargs={"pk": file_obj.pk})
        response = self.client.get(download_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["presigned_download_url"], mock_download_url)
        mock_generate_download_url.assert_called_once_with(
            file_obj.file_key,
            file_obj.name,
        )

    def test_rename_file_success(self):
        """Test successful renaming of a file."""
        file_obj = File.objects.create(
            user=self.user_a,
            file_key="user_a/test_key.txt",
            name="old_name.txt",
            size=15,
        )

        body = {"name": "new_name.txt"}
        detail_url = reverse("file-detail", kwargs={"pk": file_obj.pk})
        response = self.client.patch(detail_url, body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file_obj.refresh_from_db()
        self.assertEqual(file_obj.name, "new_name.txt")
        self.assertEqual(file_obj.file_key, "user_a/test_key.txt")

    def test_update_restricted_fields(self):
        """Test that restricted fields cannot be updated."""
        file_obj = File.objects.create(
            user=self.user_a,
            file_key="user_a/immutable_key.pdf",
            name="document.pdf",
            size=100,
        )

        detail_url = reverse("file-detail", kwargs={"pk": file_obj.pk})
        body = {
            "size": 999999,
            "file_key": "hacked/path.pdf",
            "upload_url": "http://hacked-url.com",
        }
        response = self.client.patch(detail_url, body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file_obj.refresh_from_db()
        self.assertEqual(file_obj.size, 100)
        self.assertEqual(file_obj.file_key, "user_a/immutable_key.pdf")

    @patch("files.signals.s3_service.delete_file")
    def test_delete_file_triggers_s3_deletion(self, mock_delete_file):
        """Test that deleting a file removes it from DB and triggers S3 deletion."""
        file_obj = File.objects.create(
            user=self.user_a,
            file_key="user_a/to_delete.pdf",
            name="to_delete.pdf",
            size=50,
        )

        detail_url = reverse("file-detail", kwargs={"pk": file_obj.pk})
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(File.objects.count(), 0)

        mock_delete_file.assert_called_once_with("user_a/to_delete.pdf")

    @patch("files.signals.s3_service.delete_file")
    def test_cascade_user_deletion_cleans_s3_files(self, mock_delete_file):
        """Test that deleting a user triggers S3 deletion for all their files."""
        File.objects.create(
            user=self.user_a,
            file_key="user_a/file1.pdf",
            name="file1.pdf",
            size=10,
        )
        File.objects.create(
            user=self.user_a,
            file_key="user_a/file2.pdf",
            name="file2.pdf",
            size=20,
        )

        self.user_a.delete()

        self.assertEqual(File.objects.count(), 0)
        self.assertEqual(mock_delete_file.call_count, 2)
