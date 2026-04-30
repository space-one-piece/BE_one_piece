import logging
import time
from collections import Counter
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.db import transaction
from django.db.models import Avg, QuerySet
from rest_framework.exceptions import ValidationError

from apps.analysis.client import GeminiClient
from apps.analysis.models import ImageAnalysis, ImageColorAnalysis, ImageResource, Scent
from apps.analysis.serializers.analysis_serializers import AnalysisDetailSerializer
from apps.analysis.service.color_serivce import ColorAnalysisUtil
from apps.chatbot.models import ChatbotRecommendation
from apps.chatbot.serializers import ChatbotRecommendationDetailSerializer
from apps.chatbot.services.recommendation_history_list import get_chatbot_recommendation_history
from apps.core.services.presigned_url_service import PresignedUrlService
from apps.core.utils.cloud_front import image_url_cloud
from apps.question.models import QuestionsResults
from apps.question.serializers.results_serializers import ResultWebShareSerializer
from apps.question.service.results_service import ResultsService
from apps.users.models.models import User

logger = logging.getLogger(__name__)


def _dice_coefficient(set_a: set[Any], set_b: set[Any]) -> float:
    if not set_a or not set_b:
        return 0.0

    intersection = len(set_a & set_b)
    return (2.0 * intersection) / (len(set_a) + len(set_b))


class AnalysisService:
    _TAG_WEIGHT = 0.7
    _KEYWORD_WEIGHT = 0.3
    _BASE_SCORE = 50.0
    _SCALE_FACTOR = 50.0

    @classmethod
    def _find_best_matching_scent(cls, ai_tags: list[str], ai_keywords: list[str]) -> tuple[Any, float]:
        all_scents = list(
            Scent.objects.only("id", "tags", "keywords", "is_bestseller").order_by("-is_bestseller", "id")
        )

        if not all_scents:
            return None, 0.0

        ai_tags_set = set(ai_tags)
        ai_keywords_set = set(ai_keywords)

        if not ai_tags_set and not ai_keywords_set:
            return all_scents[0], 0.0

        effective_tag_weight = cls._TAG_WEIGHT if ai_tags_set else 0.0
        effective_keyword_weight = cls._KEYWORD_WEIGHT if ai_keywords_set else 0.0
        total_weight = effective_tag_weight + effective_keyword_weight

        best_scent = all_scents[0]
        highest_score = 0.0

        for scent in all_scents:
            scent_tags_set = set(scent.tags)
            scent_keywords_set = set(scent.keywords)

            tag_sim = _dice_coefficient(ai_tags_set, scent_tags_set)
            keyword_sim = _dice_coefficient(ai_keywords_set, scent_keywords_set)

            combined_score = (
                (tag_sim * effective_tag_weight) + (keyword_sim * effective_keyword_weight)
            ) / total_weight

            if combined_score > highest_score:
                highest_score = combined_score
                best_scent = scent

        if highest_score == 0.0:
            return best_scent, 0.0

        ux_score = cls._BASE_SCORE + (highest_score * cls._SCALE_FACTOR)

        final_percentage = round(min(ux_score, 100.0), 1)

        return best_scent, final_percentage

    @staticmethod
    def image_analysis_process(user: User, img_key: str) -> tuple[ImageAnalysis, ImageColorAnalysis]:
        resource = ImageResource.objects.filter(user=user, img_key=img_key).first()
        if not resource:
            raise ValueError("유효하지 않은 이미지 키이거나 접근 권한이 없습니다.")

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
            gemini = GeminiClient(model_name=current_model, timeout=15)

            for attempt in range(max_attempt):
                try:
                    logger.info(f"[{current_model}] 모델 AI 분석 시도 ({attempt + 1}/{max_attempt})")
                    ai_result = gemini.analyze_scent_from_image(image_bytes)
                    break
                except Exception as e:
                    error_msg = str(e).lower()
                    if "timeout" in error_msg or "503" in error_msg or "unavailable" in error_msg:
                        logger.warning(f"[{current_model}] AI 서버 지연/과부하 발생 (시도 {attempt + 1})")
                    else:
                        logger.error(f"[{current_model}] 분석 중 알 수 없는 에러 발생: {e}", exc_info=True)

                    if attempt < max_attempt - 1:
                        time.sleep(2)  # 2초 대기 후 재시도
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

        img_url = resource.image_url
        with transaction.atomic():
            resource.is_uploaded = True
            resource.save()

            analysis_record = ImageAnalysis.objects.create(
                user=user,
                image_resource=resource,
                recommended_scent=best_scent,
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
            # .prefetch_related("image_metadata") 목록 조회에서 불필요
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
                "type": "image",
                "recommended_scent": {
                    "id": item.recommended_scent.id,
                    "tags": item.recommended_scent.tags,
                    "name": item.recommended_scent.name,
                    "description": item.recommended_scent.description,
                    "season": item.recommended_scent.season,
                    "eng_name": item.recommended_scent.eng_name,
                    "thumbnail_url": image_url_cloud(item.recommended_scent.thumbnail_url),
                }
                if item.recommended_scent
                else None,
                "review": item.review,
                "rating": item.rating,
                "created_at": item.created_at,
            }
            for item in image_qs
        ]

        survey_data = ResultsService.result_list(user_id, "survey")
        keyword_data = ResultsService.result_list(user_id, "keyword")
        chatbot_data = get_chatbot_recommendation_history(user_id)

        combined = image_data + survey_data + keyword_data + chatbot_data

        return sorted(combined, key=lambda x: x["created_at"], reverse=True)

    @staticmethod
    def create_upload_resource(user: User, file_name: str) -> dict[str, Any]:
        s3_result = PresignedUrlService.create(folder="analysis", file_name=file_name)

        resource = ImageResource.objects.create(
            user=user,
            img_key=s3_result["key"],
            original_name=file_name,
            is_uploaded=False,
        )

        return {
            "presigned_url": s3_result["presigned_url"],
            "img_url": s3_result["img_url"],
            "key": s3_result["key"],
            "resource_id": resource.id,
        }

    @staticmethod
    def get_my_analysis(user_id: int, analysis_id: int) -> ImageAnalysis | None:
        return (
            ImageAnalysis.objects.filter(id=analysis_id, user_id=user_id)
            .select_related("recommended_scent", "image_metadata")
            .first()
        )

    @staticmethod
    def delete_analysis(user_id: int, analysis_id: int) -> bool:
        with transaction.atomic():
            analysis = (
                ImageAnalysis.objects.filter(id=analysis_id, user_id=user_id).select_related("image_resource").first()
            )

            if not analysis:
                return False

            img_key = analysis.image_resource.img_key
            analysis.image_resource.delete()

        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION,
            )
            s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=img_key)
        except Exception:
            logger.error(f"S3 파일 삭제 실패 (Key: {img_key})", exc_info=True)

        return True

    @classmethod
    def get_total_detail(cls, user_id: int, analysis_id: int, analysis_type: str) -> tuple[Any, Any]:
        instance: Any

        if analysis_type == "image":
            instance = cls.get_my_analysis(user_id=user_id, analysis_id=analysis_id)
            return instance, AnalysisDetailSerializer

        elif analysis_type == "chatbot":
            instance = (
                ChatbotRecommendation.objects.select_related("scent")
                .filter(
                    id=analysis_id,
                    user=user_id,
                )
                .first()
            )
            return instance, ChatbotRecommendationDetailSerializer

        elif analysis_type in ["keyword", "survey"]:
            instance = ResultsService.out_results(user_id=user_id, requests_id=analysis_id, division=analysis_type)
            return instance, ResultWebShareSerializer

        else:
            raise ValidationError({"detail": f"유효하지 않은 analysis_type입니다. ({analysis_type})"})

    @staticmethod
    def update_analysis_feedback(user_id: int, analysis_id: int, analysis_type: str, status: bool) -> Any:
        if analysis_type == "image":
            analysis = ImageAnalysis.objects.filter(id=analysis_id, user_id=user_id).first()
            if not analysis:
                return None
            analysis.is_helpful = status
            analysis.save(update_fields=["is_helpful", "updated_at"])
            return analysis

        elif analysis_type == "chatbot":
            chat = ChatbotRecommendation.objects.filter(id=analysis_id, user_id=user_id).first()
            if not chat:
                return None
            chat.is_saved = status
            chat.save(update_fields=["is_saved", "updated_at"])
            return chat

        elif analysis_type in ["keyword", "survey"]:
            q_res = QuestionsResults.objects.filter(id=analysis_id, user_id=user_id).first()
            if not q_res:
                return None
            q_res.is_helpful = status
            q_res.save(update_fields=["is_helpful", "updated_at"])
            return q_res

        else:
            raise ValidationError("유효하지 않은 analysis_type입니다.")

    @classmethod
    def get_integrated_feedback_list(cls, user_id: int, analysis_type: str | None = None) -> list[Any]:
        combined: list[Any] = []
        div_to_type = {"K": "keyword", "S": "survey"}

        if analysis_type in [None, "image"]:
            img_list = list(
                ImageAnalysis.objects.select_related("recommended_scent").filter(user_id=user_id, is_helpful=True)
            )
            for img in img_list:
                setattr(img, "type", "image")
            combined.extend(img_list)

        if analysis_type in [None, "chatbot"]:
            chat_list = list(
                ChatbotRecommendation.objects.select_related("scent").filter(user_id=user_id, is_saved=True)
            )
            for chat in chat_list:
                setattr(chat, "type", "chatbot")
            combined.extend(chat_list)

        if analysis_type in [None, "keyword", "survey"]:
            q_qs = QuestionsResults.objects.select_related("scent").filter(user_id=user_id, is_helpful=True)

            if analysis_type == "keyword":
                q_qs = q_qs.filter(division="K")
            elif analysis_type == "survey":
                q_qs = q_qs.filter(division="S")

            q_list = list(q_qs)
            for q in q_list:
                db_division = getattr(q, "division", "K")
                setattr(q, "type", div_to_type.get(db_division, "keyword"))
            combined.extend(q_list)

        combined.sort(key=lambda x: getattr(x, "created_at"), reverse=True)
        return combined

    @staticmethod
    def get_user_statistics(user_id: int) -> dict[str, Any]:
        base_qs = ImageAnalysis.objects.filter(user_id=user_id)
        total_analyses = base_qs.count()

        if total_analyses == 0:
            return {
                "total_analyses": 0,
                "preferred_tags": [],
                "top_ai_keywords": [],
                "image_color_stats": {
                    "most_frequent_colors": [],
                    "average_brightness_level": "데이터 없음",
                    "average_saturation_level": "데이터 없음",
                },
            }

        data_list = base_qs.values_list(
            "recommended_scent__tags",
            "ai_keywords",
            "image_metadata__dominant_color_hex",
        )

        all_tags = []
        all_ai_keywords = []
        all_colors = []

        for tags, ai_keywords, dominant_colors in data_list:
            if tags:
                all_tags.extend(tags)
            if ai_keywords:
                all_ai_keywords.extend(ai_keywords)
            if dominant_colors:
                all_colors.extend(dominant_colors)

        preferred_tags = []
        for tag, count in Counter(all_tags).most_common(3):
            preferred_tags.append(
                {
                    "tag": tag,
                    "count": count,
                    "percentage": round((count / total_analyses) * 100, 1),
                }
            )

        top_ai_keywords = [k for k, _ in Counter(all_ai_keywords).most_common(3)]
        top_colors = [c for c, _ in Counter(all_colors).most_common(2)]

        aggs = base_qs.aggregate(
            avg_b=Avg("image_metadata__avg_brightness"), avg_s=Avg("image_metadata__avg_saturation")
        )

        # 명도
        avg_b = aggs["avg_b"] or 0
        if avg_b < 40:
            b_label = "어두운 편"
        elif avg_b < 70:
            b_label = "중간"
        else:
            b_label = "밝은 편"

        # 채도
        avg_s = aggs["avg_s"] or 0
        if avg_s < 40:
            s_label = "낮은 편"
        elif avg_s < 70:
            s_label = "중간"
        else:
            s_label = "높은 편"

        return {
            "total_analyses": total_analyses,
            "preferred_tags": preferred_tags,
            "top_ai_keywords": top_ai_keywords,
            "image_color_stats": {
                "most_frequent_colors": top_colors,
                "average_brightness_level": b_label,
                "average_saturation_level": s_label,
            },
        }
