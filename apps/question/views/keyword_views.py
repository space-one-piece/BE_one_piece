from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.keyword_serializers import KeywordPostSerializer, KeywordSerializer
from apps.question.service.keyword_service import keyword_result, keyword_select


class KeywordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        summary="키워드 조회 API",
        description="키워드 조회 API",
        examples=[value_list["200_keyword_get"], value_list["401"], value_list["404"]],
        request=KeywordSerializer,
        responses={
            200: OpenApiResponse(response=KeywordSerializer, examples=[value_list["200_keyword_get"]]),
            401: OpenApiResponse(examples=[value_list["401"]]),
            404: OpenApiResponse(examples=[value_list["404"]]),
        },
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        data = keyword_select()
        serializer = KeywordSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["quest"],
        summary="키워드 답변 API",
        description="키워드 답변 API",
        request=KeywordPostSerializer(many=True),
        responses={
            201: OpenApiResponse(response=KeywordPostSerializer(many=True), examples=[value_list["201"]]),
            400: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["400_question"]]),
            401: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["401"]]),
            404: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["404"]]),
        },
    )
    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = KeywordPostSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer_data = keyword_result(request.user.id, serializer.validated_data)

        return Response(serializer_data.data, status=status.HTTP_201_CREATED)
