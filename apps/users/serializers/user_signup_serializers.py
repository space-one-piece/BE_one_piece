from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    name = serializers.CharField(max_length=20)
    birthday = serializers.DateField()
    gender = serializers.ChoiceField(choices=["M", "F"])
    email_token = serializers.CharField(write_only=True)