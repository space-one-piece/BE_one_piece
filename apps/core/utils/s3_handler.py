# AWS S3에 실제로 연결하는 도구. boto3(AWS 서비스 전부 다룰 수 있는놈)가 presigned URL, img_url 생성
import logging
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from django.conf import settings


# AWS와 통신할 수 있는 연결 객체 만들어유
class S3Handler:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.region = settings.AWS_S3_REGION

    # presigned URL 생성
    def generate_presigned_url(self, key: str, content_type: str, expires_in: int = 300) -> str:
        return self.client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

    def generate_get_presigned_url(self, key: str, expires_in: int = 1800) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
            },
            ExpiresIn=expires_in,
        )

    # 이미지 URL 생성
    def get_img_url(self, key: str) -> str:
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"

    def s3_image(self, image_url: str | None) -> str | None:
        if not image_url:
            return None

        image_key = image_url_edit(image_url)

        if not image_key:
            return None

        try:
            return self.generate_get_presigned_url(image_key)
        except ClientError as e:
            logger = logging.getLogger(__name__)
            logger.error(e)
            return image_url

    @staticmethod
    def build_share_image_key(scent_name: str, result_id: int, division: str) -> str:
        safe_name = scent_name.replace(" ", "_")
        return f"uploads/images/share_results/{safe_name}_{result_id}_{division}.jpg"

    def check_share_image_exists(self, s3_key: str) -> bool:
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger = logging.getLogger(__name__)
            logger.error(e)
            return False

    def upload_share_image(self, image_bytes: bytes, s3_key: str) -> str:
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=image_bytes,
                ContentType="image/jpeg",
            )
            return self.get_img_url(s3_key)
        except ClientError as e:
            logger = logging.getLogger(__name__)
            logger.error(e)
            raise

    def get_or_create_share_image(
        self,
        image_bytes: bytes,
        scent_name: str,
        result_id: int,
        division: str,
    ) -> str:
        s3_key = self.build_share_image_key(scent_name, result_id, division)

        if self.check_share_image_exists(s3_key):
            return self.get_img_url(s3_key)

        return self.upload_share_image(image_bytes, s3_key)


def image_url_edit(image_url: str) -> str:
    parsed = urlparse(image_url)
    return parsed.path.lstrip("/") if parsed is not None else image_url
