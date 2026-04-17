from django.urls import include, path

from apps.users.views.login_views import LoginView
from apps.users.views.logout_views import LogoutView
from apps.users.views.refresh_token_views import RefreshTokenView
from apps.users.views.signup_views import SignUpView
from apps.users.views.user_profile_views import ProfileView
from apps.users.views.verification_views import EmailConfirmView, EmailSendView, SmsConfirmView, SmsSendView

app_name = "users"

verification_patterns = [
    # 이메일 인증 (이미지: verification/send-email, verify-email)
    path("send-email", EmailSendView.as_view(), name="email-send"),
    path("verify-email", EmailConfirmView.as_view(), name="email-confirm"),
    # 휴대폰 인증 (이미지: verification/send-sms, verify-sms)
    path("send-sms", SmsSendView.as_view(), name="sms-send"),
    path("verify-sms", SmsConfirmView.as_view(), name="sms-confirm"),
]

urlpatterns = [
    # 회원가입
    path("signup", SignUpView.as_view(), name="signup"),
    # 로그인
    path("login", LoginView.as_view(), name="login"),
    # 로그아웃
    path("logout", LogoutView.as_view(), name="logout"),
    # JWT토큰 재발급
    path("me/refresh", RefreshTokenView.as_view(), name="token_refresh"),
    # 내정보 조회
    path("me/profile", ProfileView.as_view(), name="profile"),
    # 인증 관련 include
    path("verification/", include(verification_patterns)),
]
