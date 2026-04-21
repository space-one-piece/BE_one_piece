from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.results_serializers import ResultsIntSerializer, ResultsSerializer
from apps.question.service.results_service import new_web_share, out_results, result_list, review_save, select_web_share


class ResultsCreateUrlAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        tags=["quest"],
        summary="web share 생성 API",
        description="web share 생성 API",
        request=None,
        responses={
            200: OpenApiResponse(response=ResultsSerializer, examples=[value_list["200_web_get"]]),
            401: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["401"]]),
            404: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["404"]]),
        },
    )
    def post(self, request: Request, results_id: str) -> Response:
        url = new_web_share(request.user.id, int(results_id))
        data = {"web_share_url": url}
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["quest"],
        summary="web share 조회 API",
        description="web share 조회 API",
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["200_web_get"]],
            ),
            404: OpenApiResponse(
                examples=[value_list["404"]],
            ),
            429: OpenApiResponse(
                examples=[value_list["429"]],
            ),
        },
    )
    def get(self, request: Request, results_id: str) -> Response:
        serializer = select_web_share(results_id)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        summary="리뷰 등록 API",
        description="리뷰 등록 API",
        request=ResultsIntSerializer,
        responses={
            200: OpenApiResponse(
                response=ResultsIntSerializer,
                examples=[value_list["200_review"]],
            ),
            401: OpenApiResponse(
                examples=[value_list["401"]],
            ),
            403: OpenApiResponse(
                examples=[value_list["403"]],
            ),
            404: OpenApiResponse(
                examples=[value_list["404"]],
            ),
        },
    )
    def patch(self, request: Request, results_id: int) -> Response:
        serializer = ResultsIntSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = review_save(
            request.user.id, results_id, serializer.validated_data["review"], serializer.validated_data["rating"]
        )
        return Response(data.data, status=status.HTTP_200_OK)


class ResultListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        summary=" 결과 목록 조회 API",
        description="결과 목록 조회 API",
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["200_list"]],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["401"]],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["403"]],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["404"]],
            ),
        },
    )
    def get(self, request: Request, division: str) -> Response:
        serializer_data = result_list(request.user.id, division)
        return Response(serializer_data, status=status.HTTP_200_OK)


class ResultDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        summary="결과 조회 API",
        description="결과 조회 API",
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["200_web_get"]],
            ),
            404: OpenApiResponse(
                examples=[value_list["404"]],
            ),
            429: OpenApiResponse(
                examples=[value_list["429"]],
            ),
        },
    )
    def get(self, request: Request, division: str, requests_id: int) -> Response:
        serializer_data = out_results(request.user.id, requests_id, division)
        return Response(serializer_data.data, status=status.HTTP_200_OK)
