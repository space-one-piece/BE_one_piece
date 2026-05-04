from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from apps.users.models.models import User


class passwordservice:
    @staticmethod
    def reset_password(email: str, email_uuid_token: str, new_password: str) -> None:
        cache_key = f"signup_token_{email_uuid_token}"
        cached_email = cache.get(cache_key)

        if not cached_email or cached_email != email.strip():
            raise ValidationError({"detail": "인증 토큰이 유효하지 않거나 만료되었습니다."})

        user = User.objects.filter(email=email).first()

        if user is not None:
            user.set_password(new_password)
            user.save()
            cache.delete(cache_key)
        else:
            raise ValidationError("인증 정보가 올바르지 않습니다.")
