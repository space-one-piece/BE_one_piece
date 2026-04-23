from django.db import models


# 소셜 종류
class SocialTypeChoice(models.TextChoices):
    GENERAL = "GENERAL"
    KAKAO = "K"
    NAVER = "N"
    GOOGLE = "G"


# 유저 상태
class UserStatus(models.TextChoices):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    WITHDRAWN = "WITHDRAWN"


# 탈퇴사유
class WithdrawalReason(models.TextChoices):
    NO_LONGER_NEEDED = "NO_LONGER_NEEDED", "더 이상 필요하지 않음"
    LACK_OF_INTEREST = "LACK_OF_INTEREST", "관심 부족"
    FOUND_BETTER_SERVICE = "FOUND_BETTER_SERVICE", "더 나은 서비스 발견"
    PRIVACY_CONCERNS = "PRIVACY_CONCERNS", "개인정보 보안 우려"
    POOR_SERVICE_QUALITY = "POOR_SERVICE_QUALITY", "서비스 품질 불만족"
    TECHNICAL_ISSUES = "TECHNICAL_ISSUES", "기술적 문제"
    LACK_OF_CONTENT = "LACK_OF_CONTENT", "콘텐츠 부족"
    OTHER = "OTHER", "기타"
