from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.core.models import TimeStampModel
from apps.user.choices import SocialTypeChoice, UserGender, UserStatus, WithdrawalReason


class UserManager(BaseUserManager["User"]):
    def create_user(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
        if not email:
            raise ValueError("이메일은 필수 입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields: object) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


# 사용자 테이블
class User(TimeStampModel, AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(max_length=255, unique=True, verbose_name="이메일")
    password = models.CharField(max_length=128, default="", verbose_name="비밀번호")
    name = models.CharField(max_length=30, verbose_name="이름")
    birthday = models.DateField(verbose_name="생년월일")
    social_type = models.CharField(
        max_length=10,
        choices=SocialTypeChoice,
        default="GENERAL",
        verbose_name="가입 경로",
    )
    phone_number = models.CharField(max_length=20, unique=True, verbose_name="휴대전화")
    gender = models.CharField(max_length=6, choices=UserGender, verbose_name="성별")
    status = models.CharField(choices=UserStatus, default=UserStatus.ACTIVE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone_number"]

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"

    class Meta:
        db_table = "user"
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"


# 소셜 유저
class SocialUser(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(
        max_length=20, choices=SocialTypeChoice, verbose_name="소셜 플랫폼"
    )  # KAKAO, NAVER, GOOGLE
    social_id = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "social_user"
        verbose_name = "소셜 연동 정보"


# 탈퇴 유저 정보
class UserWithdrawal(TimeStampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_withdrawal")
    reason = models.CharField(max_length=30, choices=WithdrawalReason, verbose_name="탈퇴 사유")
    other_reason = models.TextField(null=True, blank=True, verbose_name="기타 사유")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="탈퇴 신청일")
    scheduled_delete_at = models.DateTimeField(verbose_name="데이터 실제 삭제 예정일")

    def __str__(self) -> str:
        return f"{self.user.email} - {self.get_reason_display()}"

    class Meta:
        db_table = "user_withdrawal"
        verbose_name = "탈퇴 정보"
