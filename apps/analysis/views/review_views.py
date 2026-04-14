# drf-spectacular 문서화 도구
from urllib.request import Request

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.review_serializers import AnalysisReviewSerializer


class AnalysisReviewAPIView(APIView):
    @extend_schema(
        tags=["image_analysis_review"],
        summary="특정 분석의 리뷰 조회",
        responses={
            200: AnalysisReviewSerializer,
            404: OpenApiResponse(description="분석 결과를 찾을 수 없음"),
        },
    )
    def get(self, request: Request, id: int) -> Response:
        return Response(...)

    @extend_schema(
        tags=["image_analysis_review"],
        summary="분석 결과에 대한 리뷰 작성/수정",
        request=AnalysisReviewSerializer,
        responses={
            200: OpenApiResponse(description="리뷰 저장 성공"),
            400: OpenApiResponse(description="잘못된 입력값"),
        },
    )
    def patch(self, request: Request, id: int) -> Response:
        return Response(...)

    @extend_schema(
        tags=["image_analysis_review"],
        summary="작성한 리뷰 삭제",
        description="작성한 리뷰 삭제",
        responses={
            204: OpenApiResponse(description="리뷰 삭제 성공"),
            404: OpenApiResponse(description="분석글 찾을 수 없음"),
        },
    )
    def delete(self, request: Request, id: int) -> Response:
        return Response(...)
