from rest_framework_simplejwt.tokens import RefreshToken


def refresh_token_service(refresh_token_str: str) -> dict[str, str]:
    token = RefreshToken(refresh_token_str)  # type: ignore

    data = {"access": str(token.access_token), "refresh": str(token)}

    return data
