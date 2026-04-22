from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound, Throttled
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ChatbotRecommendation, ChatSession
from ..serializers import ChatbotRecommendationDetailSerializer
from ..services.chatbot_completion_policy import MAX_RETRY_COUNT
from ..services.chatbot_service import get_ai_response
from ..services.context_service import init_context
from ..services.scent_filter_service import filter_scents, get_fallback_scents
from ..views.chat_views import get_session_store, set_session_store

User = get_user_model()


class ChatbotRecommendationSaveView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot"],
        summary="추천 결과 저장",
        description="챗봇이 추천한 향수 결과를 저장합니다",
        responses={
            200: OpenApiResponse(description="저장 성공"),
            401: OpenApiResponse(description="인증 실패"),
            403: OpenApiResponse(description="접근 권한 없음"),
            404: OpenApiResponse(description="추천 결과 없음"),
        },
    )
    def patch(self, request: Request, session_id: int, recommendation_id: int) -> Response:
        user = request.user
        if not isinstance(user, User):
            raise NotAuthenticated()

        try:
            recommendation = ChatbotRecommendation.objects.get(
                id=recommendation_id,
                session_id=session_id,
                user=user,
            )
        except ChatbotRecommendation.DoesNotExist:
            raise NotFound()

        recommendation.is_saved = True
        recommendation.saved_at = now()
        recommendation.save(update_fields=["is_saved", "saved_at"])

        return Response(
            {
                "status": "success",
                "data": {
                    "recommendation_id": recommendation.id,
                    "is_saved": recommendation.is_saved,
                    "saved_at": recommendation.saved_at,
                },
            },
            status=status.HTTP_200_OK,
        )


class ChatbotRecommendationRetryStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot"],
        summary="재추천 가능 여부 조회",
        description="현재 세션의 오늘 재추천 가능 여부를 조회합니다",
        responses={
            200: OpenApiResponse(description="조회 성공"),
            401: OpenApiResponse(description="인증 실패"),
            404: OpenApiResponse(description="세션 없음"),
        },
    )
    def get(self, request: Request, session_id: int) -> Response:
        user = request.user
        if not isinstance(user, User):
            raise NotAuthenticated()

        try:
            ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            raise NotFound()

        store = get_session_store(session_id)
        if not store:
            raise NotFound()

        excluded_ids = store.get("excluded_ids", [])

        retry_count = max(len(excluded_ids) - 1, 0)
        retry_available = retry_count < MAX_RETRY_COUNT

        return Response(
            {
                "status": "success",
                "data": {
                    "retry_count": retry_count,
                    "retry_available": retry_available,
                },
            },
            status=status.HTTP_200_OK,
        )


class ChatbotRecommendationRetryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot"],
        summary="재추천 요청",
        description="현재 세션에서 다른 향수를 재추천 요청합니다",
        responses={
            200: OpenApiResponse(description="재추천 성공"),
            401: OpenApiResponse(description="인증 실패"),
            404: OpenApiResponse(description="세션 없음"),
            429: OpenApiResponse(description="재추천 횟수 초과"),
        },
    )
    def post(self, request: Request, session_id: int) -> Response:
        user = request.user
        if not isinstance(user, User):
            raise NotAuthenticated()

        try:
            session = ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            raise NotFound()

        store = get_session_store(session_id)
        if not store:
            raise NotFound()

        excluded_ids = store.get("excluded_ids", [])

        retry_count = max(len(excluded_ids) - 1, 0)

        if retry_count >= MAX_RETRY_COUNT:
            raise Throttled(detail="오늘 재추천 횟수를 초과했습니다. (최대 2회)")

        ctx = store.get("context", init_context())

        if any(v is not None for v in ctx.values()):
            candidates = filter_scents(ctx, excluded_ids)
            if not candidates:
                candidates = get_fallback_scents(excluded_ids)
        else:
            candidates = get_fallback_scents(excluded_ids)

        retry_messages = store["messages"] + [
            {"role": "user", "parts": [{"text": "방금 추천한 향수 말고 다른 향수로 재추천해주세요."}]}
        ]
        ai_response = get_ai_response(retry_messages, candidates, excluded_ids)
        reply = ai_response["reply"]
        scent_id_from_ai = ai_response["scent_id"]

        recommendation_id = None

        if scent_id_from_ai:
            with transaction.atomic():
                store["excluded_ids"].append(scent_id_from_ai)
                recommendation = ChatbotRecommendation.objects.create(
                    user=user,
                    session=session,
                    scent_id=scent_id_from_ai,
                    retry_count=retry_count + 1,
                )
                recommendation_id = recommendation.id

        # 재추천 대화 흐름 저장 (user 재추천 요청 + model 응답)
        store["messages"].append({"role": "user", "parts": [{"text": "다른 향수로 재추천해줘"}]})
        store["messages"].append({"role": "model", "parts": [{"text": reply}]})
        store["messages"] = store["messages"][-10:]
        set_session_store(session_id, store)

        return Response(
            {
                "status": "success",
                "data": {
                    "reply": reply,
                    "recommendation_id": recommendation_id,
                    "scent_id": scent_id_from_ai if recommendation_id else None,
                    "retry_count": retry_count + 1,
                    "source_type": "chatbot",
                },
            },
            status=status.HTTP_200_OK,
        )


class ChatbotRecommendationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot"],
        summary="추천 결과 상세 조회",
        description="챗봇 추천 결과 상세 정보를 조회합니다",
        responses={
            200: OpenApiResponse(description="조회 성공"),
            401: OpenApiResponse(description="인증 실패"),
            404: OpenApiResponse(description="추천 결과 없음"),
        },
    )
    def get(self, request: Request, session_id: int, recommendation_id: int) -> Response:
        user = request.user
        if not isinstance(user, User):
            raise NotAuthenticated()

        try:
            recommendation = ChatbotRecommendation.objects.select_related("scent").get(
                id=recommendation_id,
                session_id=session_id,
                user=user,
            )
        except ChatbotRecommendation.DoesNotExist:
            raise NotFound()

        serializer = ChatbotRecommendationDetailSerializer(recommendation)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
