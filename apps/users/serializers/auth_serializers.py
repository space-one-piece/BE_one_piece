from typing import Any

from rest_framework import serializers

from apps.users.choices import WithdrawalReason


# 유저 로그인 요청 데이터
class LoginSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField(label="이메일")
    password = serializers.CharField(label="비밀번호", write_only=True, style={"input_type": "password"})


# 최소한의 유저 정보 모양
class UserSimpleSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField()


# 로그인 성공 . 클라이언트가 받게 될 최종 데이터 구조
class LoginResponseSerializer(serializers.Serializer[Any]):
    access = serializers.CharField()
    refresh = serializers.CharField()


# 회원탈퇴
class UserWithdrawalSerializer(serializers.Serializer[Any]):
    password = serializers.CharField(write_only=True, label="비밀번호 확인")
    confirm = serializers.BooleanField(
        required=True, label="탈퇴 동의 여부", help_text="탈퇴에 동의해야 처리가 가능합니다."
    )
    reason = serializers.ChoiceField(choices=WithdrawalReason, label="탈퇴 사유", required=True)
    other_reason = serializers.CharField(required=False, allow_blank=True, label="기타 사유", default="")


# 계정복구
class AccountRecoverySerializer(serializers.Serializer[Any]):
    email = serializers.EmailField(label="이메일")
    password = serializers.CharField(write_only=True, style={"input_type": "password"}, label="비밀번호 확인")
    recovery_token = serializers.CharField(label="복구 토큰", help_text="이메일 인증 완료 후 발급된 UUID 토큰")
