from typing import Any

from django.db import transaction

from apps.users.models.models import User


class UserProfileUpdateService:
    @staticmethod
    def get_user_profile(user: User) -> User:
        return user

    @staticmethod
    @transaction.atomic
    def update_user_profile(user: User, data: dict[str, Any]) -> User:
        for attr, value in data.items():
            setattr(user, attr, value)
        user.save()
        return user
