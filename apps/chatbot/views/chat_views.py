from typing import Any

from django.contrib.auth import get_user_model
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import NotAuthenticated, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ChatbotRecommendation, ChatSession
from ..services.chatbot_completion_policy import (
    is_meaningful_turn,
    should_force_end,
    should_force_fallback,
    validate_chatbot_input,
)
from ..services.chatbot_service import (
    extract_recommended_scent_id,
    get_ai_response,
    parse_context,
)
from ..services.context_service import (
    can_recommend,
    init_context,
    merge_context,
)
from ..services.scent_filter_service import (
    filter_scents,
    get_fallback_scents,
)

User = get_user_model()

# 메모리 세션 저장쇼
SESSION_STORE: dict[int, dict[str, Any]] = {}


class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot"],
        summary="메시지 전송",
        description="사용자 메시지를 전송하고 AI 응답을 받습니다",
        request=inline_serializer(name="ChatMessageRequest", fields={"message": serializers.CharField()}),
        responses={
            200: OpenApiResponse(description="AI 응답 성공"),
            400: OpenApiResponse(description="메시지 없음 또는 잘못된 요청"),
            401: OpenApiResponse(description="인증 실패"),
            403: OpenApiResponse(description="접근 권한 없음"),
            404: OpenApiResponse(description="세션 없음"),
        },
    )
    def post(self, request: Request, session_id: int) -> Response:
        user = request.user
        if not isinstance(user, User):
            raise NotAuthenticated()

        # 메시지 검증
        message = request.data.get("message", "")
        validate_chatbot_input(message)

        # 세션 확인
        try:
            session = ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            raise NotFound()

        # 메모리에서 세션 데이터 가져오기
        if session_id not in SESSION_STORE:
            SESSION_STORE[session_id] = {
                "messages": [],
                "context": init_context(),
                "total_turns": 0,
                "meaningful_turns": 0,
                "excluded_ids": [],
            }

        store = SESSION_STORE[session_id]

        # 강제 종료 확인
        if should_force_end(store["total_turns"]):
            session.status = "inactive"
            session.ended_at = now()
            session.save()
            raise ValidationError()

        # 메시지 추가
        store["messages"].append({"role": "user", "content": message})
        store["total_turns"] += 1

        # 의미있는 턴 카운트 및 context 업데이트
        if is_meaningful_turn(message):
            store["meaningful_turns"] += 1
            new_ctx = parse_context(message)
            store["context"] = merge_context(store["context"], new_ctx)

        # 추천 가능 여부 판단
        is_recommendation = False
        recommendation_id = None
        candidates = None

        if can_recommend(store["context"]):
            candidates = filter_scents(store["context"], store["excluded_ids"])
        elif should_force_fallback(store["meaningful_turns"]):
            candidates = get_fallback_scents(store["excluded_ids"])

        # AI 응답 생성
        reply = get_ai_response(store["messages"], candidates)

        # 추천 결과 처리
        if candidates:
            scent_id = extract_recommended_scent_id(reply)
            if scent_id:
                is_recommendation = True
                store["excluded_ids"].append(scent_id)

                recommendation = ChatbotRecommendation.objects.create(
                    user=user,
                    session=session,
                    scent_id=scent_id,
                )
                recommendation_id = recommendation.id

        # AI 응답 메모리에 추가
        store["messages"].append({"role": "assistant", "content": reply})

        return Response(
            {
                "status": "success",
                "data": {
                    "reply": reply,
                    "is_recommendation": is_recommendation,
                    "recommendation_id": recommendation_id,
                },
            },
            status=status.HTTP_200_OK,
        )
