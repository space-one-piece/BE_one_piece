from django.urls import path

from apps.users.views.admin.admin_user_views import AdminUserListView

app_name = "admin_users"


urlpatterns = [
    # 어드민 회원 목록 조회
    path("accounts", AdminUserListView.as_view(), name="admin-list")
]
