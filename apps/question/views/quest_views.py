from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.quset_serializers import QuestionSerializer
from apps.question.service.quest_serializers import quest_select


class QuestAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["quest"],
        description="설문 조회 API",
        examples=[value_list["200_question_get"], value_list["401"]],
        responses={200: value_list["200_question_get"], 401: value_list["401"]},
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        data = quest_select()
        serializer = QuestionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["quest"],
        description="설문 답변 API",
        examples=[value_list["201"], value_list["400_question"], value_list["401"]],
        responses={201: value_list["201"], 400: value_list["400_question"], 401: value_list["401"]},
    )
    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "결과 조회"})
