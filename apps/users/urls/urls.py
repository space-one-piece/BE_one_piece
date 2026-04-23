from django.urls import include, path

from apps.users.views.auth_views import LoginView, LogoutView, UserWithdrawalView
from apps.users.views.find_email_views import FindEmailView
from apps.users.views.refresh_token_views import RefreshTokenView
from apps.users.views.reset_passwor_views import PasswordResetView
from apps.users.views.signup_views import SignUpView
from apps.users.views.social_login_views import (
    GoogleSocialLoginCallbackView,
    GoogleSocialLoginView,
    KakaoSocialLoginCallbackView,
    KakaoSocialLoginView,
    NaverSocialLoginCallbackView,
    NaverSocialLoginView,
)
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
    # 소셜 로그인
    path("social-login/naver", NaverSocialLoginView.as_view(), name="naver_social_login"),
    path("social-login/naver/callback", NaverSocialLoginCallbackView.as_view(), name="naver_social_callback"),
    path("social-login/kakao", KakaoSocialLoginView.as_view(), name="kakao_social_login"),
    path("social-login/kakao/callback", KakaoSocialLoginCallbackView.as_view(), name="kakao_social_callback"),
    path("social-login/google", GoogleSocialLoginView.as_view(), name="google_social_login"),
    path("social-login/google/callback", GoogleSocialLoginCallbackView.as_view(), name="google_social_callback"),
    # 이메일 찾기
    path("find-email", FindEmailView.as_view(), name="find_email"),
    # 비밀번호 재설정
    path("chang-password", PasswordResetView.as_view(), name="change_password"),
    # 회원탈퇴
    path("me", UserWithdrawalView.as_view(), name="me"),
    # 인증 관련 include
    path("verification/", include(verification_patterns)),
]
