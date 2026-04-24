from django.test import TestCase

from apps.analysis.models import ImageAnalysis, ImageColorAnalysis, ImageResource, Scent
from apps.analysis.serializers.analysis_serializers import AnalysisDetailSerializer, UploadURLSerializer
from apps.users.models.models import User


class SerializerValidationTest(TestCase):
    """
    프론트 입력 데이터 체크
    """

    def test_upload_url_serializer_valid(self) -> None:
        """정상적인 이미지 파일이 들어오는가"""
        data = {"file_name": "test_image.jpg", "file_type": "image/jpeg"}
        serializer = UploadURLSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_upload_url_serializer_missing_field(self) -> None:
        """image_type 누락 확인"""
        data = {"file_name": "test_image.jpg"}
        serializer = UploadURLSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file_type", serializer.errors)


class SerializerOutputTest(TestCase):
    """
    프론트 출력 테스트 체크
    """

    user: User
    scent: Scent
    analysis: ImageAnalysis
    color: ImageColorAnalysis
    image_resource: ImageResource

    @classmethod
    def setUpTestData(cls) -> None:
        """1:1 역참조 테스트 데이터 세팅"""
        cls.user = User.objects.create_user(email="test@test.com", password="password", birthday="1995-01-01")

        cls.scent = Scent.objects.create(name="우디 샌달우드", eng_name="Woody Sandalwood", intensity=4)

        cls.image_resource = ImageResource.objects.create(user=cls.user)

        cls.analysis = ImageAnalysis.objects.create(
            user=cls.user,
            recommended_scent=cls.scent,
            s3_image_url="https://s3.amazonaws.com/test.jpg",
            image_resource=cls.image_resource,
        )

        cls.color = ImageColorAnalysis.objects.create(
            analysis=cls.analysis, dominant_color_hex=["#FFFFFF", "#000000"], avg_brightness=80
        )

    def test_analysis_detail_serializer_nested_output(self) -> None:
        """향과 컬러분석 중첩데이터 확인"""
        serializer = AnalysisDetailSerializer(self.analysis)
        data = serializer.data

        self.assertIn("recommended_scent", data)
        self.assertEqual(data["recommended_scent"]["name"], "우디 샌달우드")
        self.assertIn("image_metadata", data)

        self.assertIsInstance(data["image_metadata"], dict)
        self.assertEqual(data["image_metadata"]["avg_brightness"], 80.0)
        self.assertEqual(data["image_metadata"]["dominant_color_hex"][0], "#FFFFFF")
