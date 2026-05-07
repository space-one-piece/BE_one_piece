from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.core.utils.s3_handler import S3Handler
from apps.users.models.models import User


class UserProfileUpdateService:
    @staticmethod
    def get_user_profile(user_id: int) -> User:
        user = get_object_or_404(User, id=user_id)
        user.profile_image_url = S3Handler().s3_image(user.profile_image_url)
        return user

    @staticmethod
    @transaction.atomic
    def update_user_profile(user: User, data: dict[str, Any]) -> User:
        for attr, value in data.items():
            setattr(user, attr, value)
        user.save()

        user.profile_image_url = S3Handler().s3_image(user.profile_image_url)
        return user
