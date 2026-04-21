import logging
import time
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet

from apps.analysis.client import GeminiClient
from apps.analysis.models import ImageAnalysis, ImageColorAnalysis, Scent
from apps.analysis.service.color_serivce import ColorAnalysisUtil
from apps.chatbot.services.recommendation_history_list import get_chatbot_recommendation_history
from apps.question.service.results_service import result_list
from apps.users.models.models import User

logger = logging.getLogger(__name__)


class AnalysisService:
    @staticmethod
    def _find_best_matching_scent(ai_tags: list[str], ai_keywords: list[str]) -> tuple[Scent | None, float]:
        all_scents_qs = Scent.objects.only("id", "tags", "keywords", "is_bestseller").order_by("-is_bestseller", "id")
        all_scents = list(all_scents_qs)

        if not all_scents:
            return None, 0.0

        ai_tags_set = set(ai_tags)
        ai_keywords_set = set(ai_keywords)

        tag_score = 5.0
        keyword_score = 2.0
        max_score = (len(ai_tags_set) * tag_score) + (len(ai_keywords_set) * keyword_score)

        if max_score == 0:
            return all_scents[0], 0.0

        best_scent = all_scents[0]
        highest_score = 0.0

        for scent in all_scents:
            scent_tags_set = set(scent.tags)
            scent_keywords_set = set(scent.keywords)

            matching_tags_count = len(ai_tags_set.intersection(scent_tags_set))
            matching_keywords_count = len(ai_keywords_set.intersection(scent_keywords_set))

            current_score = (matching_tags_count * tag_score) + (matching_keywords_count * keyword_score)

            if current_score > highest_score:
                highest_score = current_score
                best_scent = scent

        match_score_percentage = round((highest_score / max_score) * 100, 1)
        return best_scent, match_score_percentage

    @staticmethod
    def image_analysis_process(user: User, img_key: str) -> tuple[ImageAnalysis, ImageColorAnalysis]:
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION,
            )
            response = s3_client.get_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=img_key)
            image_bytes = response["Body"].read()
        except (BotoCoreError, ClientError):
            logger.error("S3 이미지 다운로드 실패", exc_info=True)
            raise ValueError("이미지를 불러오는데 실패했습니다.")

        ai_result = None
        model_lineup = [settings.GEMINI_MODEL, settings.SUB_GEMINI_MODEL]
        max_attempt = 2

        for current_model in model_lineup:
            gemini = GeminiClient(model_name=current_model)

            for attempt in range(max_attempt):
                try:
                    logger.info(f"[{current_model}] 모델 AI 분석 시도 ({attempt + 1}/{max_attempt})")
                    ai_result = gemini.analyze_scent_from_image(image_bytes)
                    break
                except Exception:
                    logger.warning(f"[{current_model}] 분석 실패", exc_info=True)
                    if attempt < max_attempt - 1:
                        time.sleep(2)

            if ai_result:
                break

        if not ai_result:
            logger.error("모든 AI 모델 응답 실패. Fallback(DB 추천) 응답")

            best_scent = Scent.objects.only("id").order_by("-is_bestseller", "id").first()
            match_score = 0.0

            ai_tags, ai_keywords = [], []
            ai_intensity = 3
            ai_comment = "현재 AI 분석 서버가 혼잡하여 대중적으로 인기 많은 향을 추천드립니다."
        else:
            ai_tags = ai_result.get("tags", [])
            ai_keywords = ai_result.get("keywords", [])
            ai_intensity = ai_result.get("intensity", 3)
            ai_comment = ai_result.get("comment", "")

            best_scent, match_score = AnalysisService._find_best_matching_scent(
                ai_tags=ai_tags, ai_keywords=ai_keywords
            )

        try:
            color_data = ColorAnalysisUtil.extract_colors(image_bytes)
            is_color_failed = False
            color_error_msg = None
        except Exception as e:
            logger.error("색상 추출 실패", exc_info=True)
            is_color_failed = True
            color_data = {"dominant_hex": "#FFFFFF", "contrast": 0.0, "brightness": 0.0, "saturation": 0.0}
            color_error_msg = str(e.__cause__ or e)

        img_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{img_key}"
        with transaction.atomic():
            analysis_record = ImageAnalysis.objects.create(
                user=user,
                recommended_scent=best_scent,  # type: ignore
                s3_image_url=img_url,
                ai_tags=ai_tags,
                ai_intensity=ai_intensity,
                ai_keywords=ai_keywords,
                ai_comment=ai_comment,
                match_score=match_score,
                is_fallback=not bool(ai_result),
            )

            color_record = ImageColorAnalysis.objects.create(
                analysis=analysis_record,
                dominant_color_hex=color_data["dominant_hex"],
                contrast_ratio=color_data["contrast"],
                avg_brightness=color_data["brightness"],
                avg_saturation=color_data["saturation"],
                is_failed=is_color_failed,
                error_log=color_error_msg,
            )

        return analysis_record, color_record

    @staticmethod
    def get_analysis_list(user_id: int) -> QuerySet[ImageAnalysis]:
        return (
            ImageAnalysis.objects.filter(user_id=user_id)
            .select_related("recommended_scent")
            # .prefetch_related("image_metadata")
            .order_by("-created_at")
        )

    @staticmethod
    def get_integrated_history_list(user_id: int) -> list[dict[str, Any]]:
        image_qs = (
            ImageAnalysis.objects.filter(user_id=user_id).select_related("recommended_scent").order_by("-created_at")
        )

        image_data = [
            {
                "id": item.id,
                "type": "analyses",
                "recommended_scent": {
                    "id": item.recommended_scent.id,
                    "name": item.recommended_scent.name,
                    "eng_name": item.recommended_scent.eng_name,
                    "thumbnail_url": item.recommended_scent.thumbnail_url,
                }
                if item.recommended_scent
                else None,
                "review": item.review,
                "rating": item.rating,
                "created_at": item.created_at,
            }
            for item in image_qs
        ]

        survey_data = result_list(user_id, "survey")
        keyword_data = result_list(user_id, "keywords")
        chatbot_data = get_chatbot_recommendation_history(user_id)

        combined = image_data + survey_data + keyword_data + chatbot_data

        return sorted(combined, key=lambda x: x["created_at"], reverse=True)
