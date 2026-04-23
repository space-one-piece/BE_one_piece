from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


def refresh_token_service(refresh_token_str: str) -> dict[str, str]:
    try:
        token = RefreshToken(refresh_token_str)  # type: ignore
        return {
            "access_token": str(token.access_token),
            "refresh": str(token),
        }
    except TokenError as e:
        raise e
