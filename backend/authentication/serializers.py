from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Validate that the email is unique and normalized."""
        email = value.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return email

    def validate_password(self, value):
        """Validate the password using Django's built-in validators."""
        validate_password(value)
        return value

    def create(self, validated_data):
        """Create a new user with the validated data."""
        return User.objects.create_user(**validated_data)
