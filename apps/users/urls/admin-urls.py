from django.urls import path

from apps.users.views.admin.admin_user_views import AdminUserDetailView, AdminUserListView

app_name = "admin_users"


urlpatterns = [
    # 어드민 회원 목록 조회
    path("accounts", AdminUserListView.as_view(), name="admin-list"),
    # 회원목록 상세 조회
    path("accounts/<int:account_id>", AdminUserDetailView.as_view(), name="admin-detail"),
]
