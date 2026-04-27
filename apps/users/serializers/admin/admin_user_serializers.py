from typing import Any

from rest_framework import serializers

from apps.users.models.models import User


class AdminUserListSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "birthday",
            "social_type",
            "status",
            "created_at",
        ]


class AdminUserDetailSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "phone_number",
            "birthday",
            "social_type",
            "status",
            "profile_image_url",
            "created_at",
        ]
