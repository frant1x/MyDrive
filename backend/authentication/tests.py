from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    """Test suite for user authentication endpoints."""

    def setUp(self):
        """Set up test data and URLs for authentication tests."""
        self.user_data = {
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
        }

        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("logout")

    def test_register_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())

    def test_register_duplicate_email(self):
        """Test registration with an email that already exists."""
        User.objects.create_user(**self.user_data)

        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).count() == 1)

    def test_register_weak_password(self):
        """Test registration with a weak password."""
        invalid_data = {
            "email": "weakpassword@example.com",
            "password": "123",
        }
        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(email=invalid_data["email"]).exists())

    def test_login_success(self):
        """Test successful user login."""
        User.objects.create_user(**self.user_data)

        response = self.client.post(self.login_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        User.objects.create_user(**self.user_data)
        wrong_credentials = {
            "email": self.user_data["email"],
            "password": "WrongPassword123!",
        }

        response = self.client.post(self.login_url, wrong_credentials)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_token_refresh(self):
        """Test refreshing the access token using a valid refresh token."""
        User.objects.create_user(**self.user_data)
        login_res = self.client.post(self.login_url, self.user_data)
        refresh_token = login_res.data["refresh"]
        access_token = login_res.data["access"]

        response = self.client.post(self.refresh_url, {"refresh": refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotEqual(response.data["access"], access_token)

    def test_logout_and_token_blacklist(self):
        """Test logging out and blacklisting the refresh token."""
        User.objects.create_user(**self.user_data)
        login_res = self.client.post(self.login_url, self.user_data)
        refresh_token = login_res.data["refresh"]

        logout_res = self.client.post(self.logout_url, {"refresh": refresh_token})
        self.assertEqual(logout_res.status_code, status.HTTP_200_OK)
        self.assertIsNone(logout_res.data.get("detail"))

        refresh_res = self.client.post(self.refresh_url, {"refresh": refresh_token})
        self.assertEqual(refresh_res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(refresh_res.data["detail"], "Token is blacklisted")
