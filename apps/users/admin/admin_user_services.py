from django.shortcuts import get_object_or_404

from apps.users.models.models import User


class AdminUserService:
    @staticmethod
    def delete_user_admin(account_id: int) -> int:
        user = get_object_or_404(User, id=account_id)
        user.delete()
        return account_id

    @staticmethod
    def lock_user_admin(account_id: int) -> int:
        user = get_object_or_404(User, id=account_id)
        user.is_active = False
        user.status = "DEACTIVATED"
        user.save()
        return account_id
