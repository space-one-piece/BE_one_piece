from typing import Any

from django.views import View
from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request


class IsSelfOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or request.user.id is None:
            raise NotAuthenticated(detail={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})
        return True

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or request.user.id is None:
            return False

        is_staff = request.user.is_staff

        if obj.author_id != request.user.id and not is_staff:
            raise PermissionDenied(detail={"error_detail": "권한이 없습니다."})
        return True
