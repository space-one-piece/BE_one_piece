import logging
import urllib.parse
from typing import Any, cast

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.services.social_login_services import GoogleOAuthService, KaKaoOAuthService, NaverOAuthService

logger = logging.getLogger(__name__)


def frontend_redirect(*, provider: str, is_success: bool = True, **kwargs: Any) -> HttpResponseRedirect:
    base = getattr(settings, "FRONTEND_SOCIAL_REDIRECT_URL", "http://localhost:5173")

    if is_success:
        params = kwargs
    else:
        params = {"provider": provider, "is_success": "false"}
        params.update(kwargs)

    query_string = urllib.parse.urlencode(params)
    url = f"{base}/?{query_string}" if not base.endswith("/") else f"{base}?{query_string}"
    return redirect(url)


def set_auth_cookies(response: Any, refresh: str) -> None:
    response.set_cookie(
        "refresh_token",
        refresh,
        max_age=7 * 24 * 60 * 60,
        domain=getattr(settings, "COOKIE_DOMAIN", None),
        httponly=True,
        secure=getattr(settings, "COOKIE_SECURE", False),
        samesite="Lax",
        path="/",
    )


# 네이버 뷰
class NaverSocialLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="네이버 로그인 시작",
        tags=["accounts"],
        description=(
            "## 프론트엔드 사용법\n\n"
            "1. 네이버 로그인 버튼 클릭 시 이 URL로 GET 요청\n"
            "2. 네이버 인증 페이지로 자동 리다이렉트됨\n"
            "3. 유저가 네이버 로그인 완료 → 콜백 URL로 자동 이동\n"
            "4. 콜백 처리 후 프론트 {FRONTEND_SOCIAL_REDIRECT_URL}?provider=kakao&is_success=true로 리다이렉트\n"
            "5. refresh_token이 쿠키(httponly)에 세팅됨\n"
            "6. 프론트에서 POST /api/v1/accounts/me/refresh를 호출하여 access_token을 발급받아 사용\n\n"
            "[네이버 로그인 테스트 (클릭)](/api/v1/accounts/social-login/naver)"
        ),
        responses={
            302: OpenApiResponse(description="네이버 인증 페이지로 리다이렉트"),
        },
    )
    def get(self, request: Request) -> Any:
        service = NaverOAuthService()
        auth_url, state = service.get_auth_url()
        request.session["social_login_state"] = state
        return redirect(auth_url)


class NaverSocialLoginCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="네이버 로그인 콜백",
        tags=["accounts"],
        description=(
            "네이버 인증 완료 후 네이버가 자동으로 호출하는 콜백 엔드포인트입니다.\n\n"
            "프론트에서 직접 호출할 필요 없음.\n\n"
            "처리 완료 후 프론트로 리다이렉트되며, refresh_token이 쿠키에 세팅됩니다.\n"
            "프론트에서 POST /api/v1/accounts/me/refresh 호출 → access_token 발급받아 사용."
        ),
        parameters=[
            OpenApiParameter("code", str, description="네이버 인가 코드 (네이버가 전달)"),
            OpenApiParameter("state", str, description="CSRF 방지용 상태 값 (네이버가 전달)"),
        ],
        responses={
            302: OpenApiResponse(description="프론트엔드로 리다이렉트 + refresh_token 쿠키 세팅"),
        },
    )
    def get(self, request: Request) -> Any:
        try:
            code = request.query_params.get("code")
            state = request.query_params.get("state")
            saved_state = request.session.get("social_login_state")

            if not code or state != saved_state:
                return frontend_redirect(provider="naver", is_success=False)

            service = NaverOAuthService()
            access_token = service.get_access_token(code or "", cast(str, state))
            user_info = service.get_token_info(access_token)
            user = service.get_or_create_user(user_info)

            refresh = RefreshToken.for_user(user)
            response = frontend_redirect(provider="naver", is_success=True, code=code)
            set_auth_cookies(response, refresh=str(refresh))
            return response
        except Exception:
            logger.exception("naver callback error")
            return frontend_redirect(provider="naver", is_success=False)
        finally:
            request.session.pop("social_login_state", None)


# 카카오 뷰
class KakaoSocialLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="카카오 로그인 시작",
        tags=["accounts"],
        description=(
            "## 프론트엔드 사용법\n\n"
            "1. 카카오 로그인 버튼 클릭 시 이 URL로 GET 요청\n"
            "2. 카카오 인증 페이지로 자동 리다이렉트됨\n"
            "3. 유저가 카카오 로그인 완료 → 콜백 URL로 자동 이동\n"
            "4. 콜백 처리 후 프론트 {FRONTEND_SOCIAL_REDIRECT_URL}?provider=kakao&is_success=true로 리다이렉트\n"
            "5. refresh_token이 쿠키(httponly)에 세팅됨\n"
            "6. 프론트에서 POST /api/v1/accounts/me/refresh를 호출하여 access_token을 발급받아 사용\n\n"
            "[카카오 로그인 테스트 (클릭)](/api/v1/accounts/social-login/kakao)"
        ),
        responses={
            302: OpenApiResponse(description="카카오 인증 페이지로 리다이렉트"),
        },
    )
    def get(self, request: Request) -> Any:
        service = KaKaoOAuthService()
        auth_url, state = service.get_auth_url()
        request.session["social_login_state"] = state
        return redirect(auth_url)


class KakaoSocialLoginCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="카카오 콜백",
        tags=["accounts"],
        description=(
            "카카오 인증 완료 후 네이버가 자동으로 호출하는 콜백 엔드포인트입니다.\n\n"
            "프론트에서 직접 호출할 필요 없음.\n\n"
            "처리 완료 후 프론트로 리다이렉트되며, refresh_token이 쿠키에 세팅됩니다.\n"
            "프론트에서 POST /api/v1/accounts/me/refresh 호출 → access_token 발급받아 사용."
        ),
        parameters=[
            OpenApiParameter("code", str, description="카카오 인가 코드 (카카오가 전달)"),
            OpenApiParameter("state", str, description="CSRF 방지용 상태 값 (카카오가 전달)"),
        ],
        responses={
            302: OpenApiResponse(description="프론트엔드로 리다이렉트 + refresh_token 쿠키 세팅"),
        },
    )
    def get(self, request: Request) -> Any:
        try:
            code = request.query_params.get("code")
            state = request.query_params.get("state")
            saved_state = request.session.get("social_login_state")

            if not code or state != saved_state:
                return frontend_redirect(provider="kakao", is_success=False)

            service = KaKaoOAuthService()
            access_token = service.get_access_token(code or "", cast(str, state))
            user_info = service.get_token_info(access_token)
            user = service.get_or_create_user(user_info)

            refresh = RefreshToken.for_user(user)
            response = frontend_redirect(provider="kakao", is_success=True, code=code)
            set_auth_cookies(response, refresh=str(refresh))
            return response
        except Exception:
            logger.exception("kakao callback error")
            return frontend_redirect(provider="kakao", is_success=False)
        finally:
            request.session.pop("social_login_state", None)


# 구글 로그인 뷰
class GoogleSocialLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="구글 로그인 시작",
        tags=["accounts"],
        description=(
            "## 프론트엔드 사용법\n\n"
            "1. 구글 로그인 버튼 클릭 시 이 URL로 GET 요청\n"
            "2. 구글 인증 페이지로 자동 리다이렉트됨\n"
            "3. 유저가 구글 로그인 완료 → 콜백 URL로 자동 이동\n"
            "4. 콜백 처리 후 프론트 {FRONTEND_SOCIAL_REDIRECT_URL}?provider=kakao&is_success=true로 리다이렉트\n"
            "5. refresh_token이 쿠키(httponly)에 세팅됨\n"
            "6. 프론트에서 POST /api/v1/accounts/me/refresh를 호출하여 access_token을 발급받아 사용\n\n"
            "[구글 로그인 테스트 (클릭)](/api/v1/accounts/social-login/google)"
        ),
        responses={
            302: OpenApiResponse(description="구글 인증 페이지로 리다이렉트"),
        },
    )
    def get(self, request: Request) -> Any:
        service = GoogleOAuthService()
        auth_url, state = service.get_auth_url()
        request.session["social_login_state"] = state
        return redirect(auth_url)


class GoogleSocialLoginCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="구글 콜백",
        tags=["accounts"],
        description=(
            "구글 인증 완료 후 네이버가 자동으로 호출하는 콜백 엔드포인트입니다.\n\n"
            "프론트에서 직접 호출할 필요 없음.\n\n"
            "처리 완료 후 프론트로 리다이렉트되며, refresh_token이 쿠키에 세팅됩니다.\n"
            "프론트에서 POST /api/v1/accounts/me/refresh 호출 → access_token 발급받아 사용."
        ),
        parameters=[
            OpenApiParameter("code", str, description="구글 인가 코드 (구글 전달)"),
            OpenApiParameter("state", str, description="CSRF 방지용 상태 값 (구글 전달)"),
        ],
        responses={
            302: OpenApiResponse(description="프론트엔드로 리다이렉트 + refresh_token 쿠키 세팅"),
        },
    )
    def get(self, request: Request) -> Any:
        try:
            code = request.query_params.get("code")
            state = request.query_params.get("state")
            saved_state = request.session.get("social_login_state")

            if not code or state != saved_state:
                return frontend_redirect(provider="google", is_success=False)

            service = GoogleOAuthService()
            access_token = service.get_access_token(code or "", cast(str, state))
            user_info = service.get_token_info(access_token)
            user = service.get_or_create_user(user_info)

            refresh = RefreshToken.for_user(user)
            response = frontend_redirect(provider="google", is_success=True, code=code)
            set_auth_cookies(response, refresh=str(refresh))
            return response
        except Exception:
            logger.exception("google callback error")
            return frontend_redirect(provider="google", is_success=False)
        finally:
            request.session.pop("social_login_state", None)
