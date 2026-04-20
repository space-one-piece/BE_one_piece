import json
import re
from typing import Any

import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..exceptions import SessionExpiredError, SessionInactiveError
from ..models import ChatbotRecommendation, ChatSession
from ..services.chatbot_completion_policy import (
    is_impatient,
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

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
)

SESSION_TTL = 1200


def get_session_store(session_id: int) -> dict[str, Any] | None:
    data = redis_client.get(f"chatbot:session:{session_id}")
    if data is None:
        return None
    assert isinstance(data, str)
    result: dict[str, Any] = json.loads(data)
    return result


def set_session_store(session_id: int, store: dict[str, Any]) -> None:
    redis_client.setex(
        f"chatbot:session:{session_id}",
        SESSION_TTL,
        json.dumps(store),
    )


def delete_session_store(session_id: int) -> None:
    redis_client.delete(f"chatbot:session:{session_id}")


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

        # 세션 상태 체크
        if session.status == "inactive":
            raise SessionInactiveError()

        # Redis에서 세션 데이터 가져오기
        store = get_session_store(session_id)
        if store is None:
            store = {
                "messages": [],
                "context": init_context(),
                "total_turns": 0,
                "meaningful_turns": 0,
                "excluded_ids": [],
            }

        # 강제 종료 확인
        if should_force_end(store["total_turns"]):
            session.status = "inactive"
            session.ended_at = now()
            session.save()
            delete_session_store(session_id)
            raise SessionExpiredError()

        # 메시지 추가
        store["messages"].append({"role": "user", "parts": [{"text": message}]})
        store["total_turns"] += 1
        store["messages"] = store["messages"][-10:]

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
        elif should_force_fallback(store["meaningful_turns"]) or is_impatient(message):
            candidates = get_fallback_scents(store["excluded_ids"])

        # AI 응답 생성
        reply = get_ai_response(store["messages"], candidates)
        clean_reply = re.sub(r"\[ID:\s*\d+\]\s*", "", reply)

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

        # AI 응답 Redis에 저장
        store["messages"].append({"role": "model", "parts": [{"text": reply}]})
        store["messages"] = store["messages"][-10:]
        set_session_store(session_id, store)

        return Response(
            {
                "status": "success",
                "data": {
                    "reply": clean_reply,
                    "is_recommendation": is_recommendation,
                    "recommendation_id": recommendation_id,
                    "source_type": "chatbot",
                },
            },
            status=status.HTTP_200_OK,
        )
