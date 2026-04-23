from typing import Any

from rest_framework import serializers


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

# 로그아웃
class LogoutSerializer(serializers.Serializer[Any]):
    refresh = serializers.CharField(help_text="로그아웃할 사용자의 Refresh token")
