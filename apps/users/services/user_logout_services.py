from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutService:
    @staticmethod
    def logout(refresh_token_str: str) -> None:
        try:
            token = RefreshToken(refresh_token_str)  # type: ignore
            token.blacklist()
        except Exception:
            raise ValidationError({"code": "invalid_token", "message": "유효하지 않거나 이미 만료된 토큰입니다."})
