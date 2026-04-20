from django.contrib.auth import get_user_model
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import ChatSession
from ..serializers import ChatSessionCreateSerializer, ChatSessionSerializer
from .chat_views import SESSION_STORE

User = get_user_model()


class ChatSessionCreateView(GenericAPIView[ChatSession]):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSessionCreateSerializer

    @extend_schema(
        tags=["Chatbot"],
        summary="세션 생성",
        description="첫 메시지 전송 시 채팅 세션을 생성합니다",
        responses={
            201: OpenApiResponse(description="세션 생성 성공"),
            400: OpenApiResponse(description="메시지 없음"),
            401: OpenApiResponse(description="인증 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError("메시지를 입력해주세요.")

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

        if session_id in SESSION_STORE:
            del SESSION_STORE[session_id]

        return Response(
            {"status": "success", "data": {"session_id": session.id, "ended_at": session.ended_at}},
            status=status.HTTP_200_OK,
        )
