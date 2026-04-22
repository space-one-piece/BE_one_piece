from django.contrib.auth import get_user_model
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import ChatSession
from ..serializers import ChatSessionSerializer
from ..views.chat_views import delete_session_store

User = get_user_model()


class ChatSessionCreateView(GenericAPIView[ChatSession]):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot"],
        summary="세션 생성",
        description="챗봇 페이지 진입 시 채팅 세션을 생성합니다",
        responses={
            201: OpenApiResponse(description="세션 생성 성공"),
            401: OpenApiResponse(description="인증 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        user = request.user
        if not isinstance(user, User):
            raise NotAuthenticated()

        session = ChatSession.objects.create(user=user, status="active")

        return Response(
            {"status": "success", "data": ChatSessionSerializer(session).data},
            status=status.HTTP_201_CREATED,
        )


class ChatSessionEndView(GenericAPIView[ChatSession]):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot"],
        summary="세션 종료",
        description="X버튼 클릭 또는 타임아웃 시 세션을 종료합니다",
        responses={
            200: OpenApiResponse(description="세션 종료 성공"),
            401: OpenApiResponse(description="인증 실패"),
            403: OpenApiResponse(description="접근 권한 없음"),
            404: OpenApiResponse(description="세션 없음"),
        },
    )
    def patch(self, request: Request, session_id: int) -> Response:
        user = request.user
        if not isinstance(user, User):
            raise NotAuthenticated()

        try:
            session = ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            raise NotFound()

        if session.user != user:
            raise PermissionDenied()

        session.status = "inactive"
        session.ended_at = now()
        session.save()

        delete_session_store(session_id)

        return Response(
            {"status": "success", "data": {"session_id": session.id, "ended_at": session.ended_at}},
            status=status.HTTP_200_OK,
        )
