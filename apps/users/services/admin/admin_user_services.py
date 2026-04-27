from typing import Optional

from django.db.models import Q, QuerySet
from rest_framework.generics import get_object_or_404

from apps.users.models.models import User


class AdminUserService:
    @staticmethod
    def get_user_list_admin(search_keyword: Optional[str] = None, status: Optional[str] = None) -> QuerySet[User]:
        queryset = User.objects.all().order_by("-id")

        if search_keyword:
            queryset = queryset.filter(
                Q(name__icontains=search_keyword)
                | Q(email__icontains=search_keyword)
                | Q(phone_number__icontains=search_keyword)
            )

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    @staticmethod
    def get_user_detail_admin(account_id: int) -> User:
        return get_object_or_404(User, id=account_id)
