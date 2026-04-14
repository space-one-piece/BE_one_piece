from django.test import TestCase

from apps.analysis.models import ImageAnalysis, ImageColorAnalysis, Scent
from apps.users.models.models import User


class AnalysisModelsTest(TestCase):
    user: User
    scent: Scent

    @classmethod
    def setUpTestData(cls) -> None:
        """
        테스트 유저,향 데이터
        """
        cls.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123!", birthday="1995-01-01"
        )

        cls.scent = Scent.objects.create(
            name="테스트 향수",
            eng_name="Test Scent",
            categories="Floral",
            intensity=3,
            season=["spring", "fall"],
            tags=["포근함", "우디향"],
        )

    def test_scent_creation_and_defaults(self) -> None:
        """
        향 모델의 keywords 빈값 체크, season 값 체크
        """
        self.assertEqual(self.scent.name, "테스트 향수")

        self.assertEqual(self.scent.keywords, [])
        self.assertEqual(len(self.scent.season or []), 2)

    def test_image_analysis_creation_and_defaults(self) -> None:
        """
        이미지 분석
        외래키 연결확인, default 값 체크
        """
        analysis = ImageAnalysis.objects.create(
            user=self.user,
            recommended_scent=self.scent,
            s3_image_url="https://s3.amazonaws.com/test.jpg",
            match_score=92.5,
        )

        self.assertEqual(analysis.user, self.user)
        self.assertEqual(analysis.recommended_scent, self.scent)

        self.assertFalse(analysis.is_helpful)
        self.assertFalse(analysis.is_fallback)
        self.assertIsNone(analysis.review)

    def test_image_color_analysis_creation(self) -> None:
        """
        컬러 테이블
        값 체크
        """
        analysis = ImageAnalysis.objects.create(user=self.user, recommended_scent=self.scent)
        color_analysis = ImageColorAnalysis.objects.create(
            analysis=analysis,
            dominant_color_hex=["#FFFFFF", "#000000"],
            contrast_ratio=12.3,
            avg_brightness=85.0,
            avg_saturation=12.5,
        )

        self.assertEqual(color_analysis.analysis, analysis)
        self.assertEqual(len(color_analysis.dominant_color_hex or []), 2)
        self.assertEqual(color_analysis.contrast_ratio, 12.3)
        self.assertFalse(color_analysis.is_failed)

    def test_cascade_delete_behavior(self) -> None:
        """
        유저 삭제 시 분석데이터도 삭제되는지 확인
        """
        analysis = ImageAnalysis.objects.create(user=self.user, recommended_scent=self.scent)
        ImageColorAnalysis.objects.create(analysis=analysis, avg_brightness=50.0)

        self.assertEqual(ImageAnalysis.objects.count(), 1)
        self.assertEqual(ImageColorAnalysis.objects.count(), 1)

        self.user.delete()

        self.assertEqual(ImageAnalysis.objects.count(), 0)
        self.assertEqual(ImageColorAnalysis.objects.count(), 0)
