from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.results_serializers import (
    ResultImageSerializer,
    ResultsIntSerializer,
    ResultsOutSerializer,
    ResultsSerializer,
    ResultWebShareSerializer,
    ShareOutSerializer,
    ShareSerializer,
)
from apps.question.service.image_user_service import ImageUserService
from apps.question.service.results_service import ResultsService


class ShareCreateUrlAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["share"],
        summary="web share 생성 API",
        description="web share 생성 API",
        request=ShareSerializer,
        responses={
            201: OpenApiResponse(response=ShareSerializer, examples=[value_list["201_web_post"]]),
            401: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["401"]]),
            404: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["404"]]),
        },
    )
    def post(self, request: Request) -> Response:
        result_id = request.data.get("result_id")
        type_data = request.data.get("type")

        if result_id is None or type_data is None:
            raise Http404

        url = ResultsService.new_web_share(type_data, result_id)
        serializer = ResultsSerializer(url)
        ImageUserService.web_share(
            result_id=result_id,
            division=type_data,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShareViewAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["share"],
        summary="web share 조회 API",
        description="web share 조회 API",
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["200_web_get"]],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["404"]],
            ),
            410: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["410"]],
            ),
        },
    )
    def get(self, request: Request, share_id: str) -> Response:
        serializer = ResultsService.select_web_share(share_id)
        serializer_data = ShareOutSerializer(serializer)
        return Response(serializer_data.data, status=status.HTTP_200_OK)


class ReviewViewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        summary="리뷰 등록 API",
        description="리뷰 등록 API",
        request=ResultsIntSerializer,
        responses={
            201: OpenApiResponse(
                response=ResultsIntSerializer,
                examples=[value_list["201_review"]],
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
    def patch(self, request: Request, results_id: int) -> Response:
        serializer = ResultsIntSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = ResultsService.review_save(
            request.user.id, results_id, serializer.validated_data["review"], serializer.validated_data["rating"]
        )
        data = ResultsOutSerializer(serializer_data)
        return Response(data.data, status=status.HTTP_201_CREATED)


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
        serializer_data = ResultsService.result_list(request.user.id, division)
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
                response=OpenApiTypes.OBJECT,
                examples=[value_list["404"]],
            ),
            429: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["429"]],
            ),
        },
    )
    def get(self, request: Request, division: str, requests_id: int) -> Response:
        serializer_data = ResultsService.out_results(request.user.id, requests_id, division)
        data = ResultWebShareSerializer(serializer_data)

        return Response(data.data, status=status.HTTP_200_OK)


class ResultImageAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["quest"],
        summary="결과 이미지 생성 API",
        description="결과 이미지 생성 API",
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["200_web_image"]],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["404"]],
            ),
            429: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["429"]],
            ),
        },
    )
    def post(self, request: Request, results_id: int, division: str) -> Response:
        byte = ImageUserService.web_share(results_id, division)
        serializer = ResultImageSerializer(data=byte)
        serializer.is_valid()

        return Response(serializer.data, status=status.HTTP_200_OK)
