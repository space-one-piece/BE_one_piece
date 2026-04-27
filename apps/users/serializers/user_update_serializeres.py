from typing import Any

from rest_framework import serializers

from apps.users.models.models import User


class UserProfileUpdateSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = User
        fields = ["name", "birthday", "profile_image_url", "updated_at"]


class ProfileImageUpdateSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = User
        fields = ["profile_image_url"]
