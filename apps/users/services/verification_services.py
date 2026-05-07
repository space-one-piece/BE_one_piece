import random
import string
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from solapi import SolapiMessageService  # type: ignore
from solapi.model import RequestMessage  # type: ignore


class VerificationService:
    EXPIRY_TIME = 300
    TOKEN_EXPIRY_TIME = 600

    @classmethod
    def _generate_code(cls) -> str:
        return "".join(random.choices(string.digits, k=6))

    # Email logic
    @classmethod
    def send_email_code(cls, email: str) -> bool:
        email = email.strip()  # 공백 제거
        code = cls._generate_code()
        cache.set(f"email_code_{email}", code, timeout=cls.EXPIRY_TIME)

        # 실제 발송 (테스트 시 콘솔 확인 가능)
        result = send_mail(
            subject="[Space one-piece] 이메일 인증번호",
            message=f"인증 번호는 {code} 입니다.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return bool(result)

    # phone logic
    @classmethod
    def send_phone_code(cls, phone_number: str) -> bool:
        code = cls._generate_code()
        clean_number = phone_number.replace("-", "")

        cache.set(f"phone_code_{clean_number}", code, timeout=cls.EXPIRY_TIME)

        if settings.COOLSMS_API_KEY and settings.COOLSMS_API_SECRET:
            try:
                message_service = SolapiMessageService(
                    api_key=settings.COOLSMS_API_KEY,
                    api_secret=settings.COOLSMS_API_SECRET,
                )
                message = RequestMessage(
                    from_=settings.COOLSMS_PHONE_NUMBER, to=clean_number, text=f"[한조각] 인증번호는 [{code}] 입니다."
                )

                response = message_service.send(message)
                print(f"SOLAPI 메시지 발송 성공: {response.group_info.group_id}")
                return True
            except Exception as e:
                print(f"SOLAPI 메시지 발송 실패: {str(e)}")
                return False

        # API키가 빠져버렸을 경우 if문 건너띄어서 여기(혹시 몰라서 코드 작성)
        print(f"\n[SMS 시뮬레이션] 번호: {clean_number} | 인증번호: [{code}]")
        return True

    # 공통 확인 로직(토큰 발행)
    @classmethod
    def confirm_code(cls, identifier: str, code: str, auth_type: str) -> str | None:
        if auth_type not in ["email", "phone"]:
            return None

        clean_id = identifier.strip()
        if auth_type == "phone":
            clean_id = clean_id.replace("-", "")

        cache_key = f"{auth_type}_code_{clean_id}"
        saved_code = cache.get(cache_key)

        if saved_code and str(saved_code) == str(code):
            token = str(uuid.uuid4())
            cache.set(f"signup_token_{token}", clean_id, timeout=cls.TOKEN_EXPIRY_TIME)

            cache.delete(cache_key)
            return token
        return None
