from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers

from apps.users.models.models import User


class SignUpSerializer(serializers.ModelSerializer[User]):
    email = serializers.EmailField(
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                "유효한 이메일 형식이 아닙니다.",
                code="INVALID_EMAIL_FORMAT",
            )
        ],
        error_messages={
            "unique": "이미 가입된 이메일입니다.",
        },
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])
    name = serializers.CharField(max_length=20)
    birthday = serializers.DateField()
    phone_number = serializers.CharField(
        min_length=11, max_length=11, validators=[RegexValidator(r"^\d{11}$", "휴대전화 번호는 11자리여야 합니다.")]
    )
    email_uuid_token = serializers.CharField(write_only=True)
    sms_uuid_token = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "name", "birthday", "phone_number", "email_uuid_token", "sms_uuid_token")
        extra_kwargs = {"email": {"error_messages": {"unique": "이미 가입된 이메일입니다."}}}
