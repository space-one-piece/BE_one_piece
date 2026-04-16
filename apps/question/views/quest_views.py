from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.quset_serializers import QuestionSerializer, QuestionsInSerializer
from apps.question.service.quest_service import quest_in, quest_select


class QuestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        summary="설문 조회 API",
        description="설문 조회 API",
        request=QuestionSerializer,
        responses={
            200: OpenApiResponse(response=QuestionSerializer, examples=[value_list["200_question_get"]]),
            401: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["401"]]),
        },
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        data = quest_select()
        serializer = QuestionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["quest"],
        summary="설문 답변 API",
        description="설문 답변 API",
        request=QuestionsInSerializer,
        responses={
            201: OpenApiResponse(response=QuestionSerializer, examples=[value_list["201"]]),
            400: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["400_question"]]),
            401: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["401"]]),
        },
    )
    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = QuestionsInSerializer(request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer_data = quest_in(request.user.id, serializer.validated_data)

        return Response(serializer_data, status=status.HTTP_201_CREATED)
