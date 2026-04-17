from typing import Any

from rest_framework import serializers

from apps.users.models.models import User


class UserProfileSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = User
        fields = ["name", "email", "phone_number", "birthday", "profile_image_url"]
