from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from apps.users.models.models import User


class FindEmailService:
    @staticmethod
    def find_email(name: str, phone_number: str, sms_token: str) -> str:
        cached_phone = cache.get(f"signup_token_{sms_token}")

        if not cached_phone or cached_phone != phone_number:
            raise ValidationError("인증 정보가 만료되었거나 올바르지 않습니다.")

        try:
            user = User.objects.get(name=name, phone_number=phone_number)
        except User.DoesNotExist:
            raise ValidationError("일치하는 사용자 정보가 없습니다.")

        cache.delete(f"signup_token_{sms_token}")
        return FindEmailService._mask_email(user.email)

    @staticmethod
    def _mask_email(email: str) -> str:
        try:
            id_part, domain = email.split("@")
            if len(id_part) <= 2:
                masked_id = id_part[0] + "*"
            else:
                masked_id = id_part[:2] + "*" * (len(id_part) - 2)
            return f"{masked_id}@{domain}"
        except ValueError:
            return "*****@*****.***"
