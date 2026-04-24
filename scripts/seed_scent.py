import json
import os
from typing import Any

import boto3
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.conf import settings  # noqa: E402

from apps.analysis.models import Scent  # noqa: E402

BUCKET_NAME = "one-pieced"
S3_KEY = "data/scent-mock-data-30-final.json"
REGION = "ap-northeast-2"


def load_json_from_s3() -> list[dict[str, Any]]:
    s3 = boto3.client(
        "s3",
        region_name=REGION,
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
    )
    response = s3.get_object(Bucket=BUCKET_NAME, Key=S3_KEY)
    content = response["Body"].read().decode("utf-8")
    data: list[dict[str, Any]] = json.loads(content)
    return data


def seed_scents() -> None:
    print("📦 S3에서 데이터 로드 중...")
    data = load_json_from_s3()
    print(f"✅ {len(data)}개 향기 데이터 로드 완료\n")

    updated_count = 0
    created_count = 0

    for item in data:
        obj, created = Scent.objects.update_or_create(
            eng_name=item["eng_name"],
            defaults={
                "name": item["name"],
                "description": item.get("description", ""),
                "categories": item["categories"],
                "tags": item.get("tags", []),
                "intensity": item["intensity"],
                "is_bestseller": item.get("is_bestseller", False),
                "scent_notes": item.get("scent_notes", {}),
                "profile": item.get("profile", {}),
                "season": item.get("season", []),
                "recommended_places": item.get("recommended_places", []),
                "similar_scents": item.get("similar_scents", []),
                "thumbnail_url": item.get("thumbnail_url", ""),
            },
        )

        if created:
            created_count += 1
            print(f"  ✅ 생성: {item['eng_name']}")
        else:
            updated_count += 1
            print(f"  🔄 업데이트: {item['eng_name']}")

    print(f"\n🎉 완료! 생성: {created_count}개 / 업데이트: {updated_count}개")


if __name__ == "__main__":
    seed_scents()
