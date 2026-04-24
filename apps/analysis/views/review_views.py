from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.review_serializers import AnalysisReviewSerializer
from ..service.review_service import ReviewService


class MyReviewListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    type_param = OpenApiParameter(
        name="type",
        type=str,
        required=False,
        description="조회할 리뷰 타입 (image, chatbot, keyword, survey). 목록 조회시 비워두면 전체 반환.",
    )

    @extend_schema(
        tags=["analysis_reviews"],
        summary="리뷰 목록 조회 또는 특정 리뷰 상세 조회",
        parameters=[type_param],
        responses={200: AnalysisReviewSerializer(many=True)},
    )
    def get(self, request: Request, id: int | None = None) -> Response:
        analysis_type = request.query_params.get("type")

        if id is None:
            reviews = ReviewService.get_my_reviews(user_id=request.user.id, analysis_type=analysis_type)
            return Response(AnalysisReviewSerializer(reviews, many=True).data)

        if not analysis_type:
            analysis_type = "image"

        instance = ReviewService.get_review(analysis_id=id, user=request.user, analysis_type=analysis_type)  # type: ignore
        return Response(AnalysisReviewSerializer(instance).data)

    @extend_schema(
        tags=["analysis_reviews"],
        summary="리뷰 작성 및 수정",
        parameters=[type_param],
        request=AnalysisReviewSerializer,
        responses={200: AnalysisReviewSerializer},
    )
    def patch(self, request: Request, id: int) -> Response:
        analysis_type = request.query_params.get("type", "image")
        serializer = AnalysisReviewSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated = ReviewService.patch_review(
            analysis_id=id,
            user=request.user,  # type: ignore
            analysis_type=analysis_type,
            data=serializer.validated_data,
        )
        return Response(AnalysisReviewSerializer(updated).data)

    @extend_schema(
        tags=["analysis_reviews"],
        summary="리뷰 삭제 (초기화)",
        parameters=[type_param],
        responses={204: OpenApiResponse(description="삭제 성공")},
    )
    def delete(self, request: Request, id: int) -> Response:
        analysis_type = request.query_params.get("type", "image")
        ReviewService.delete_review(id, request.user, analysis_type)  # type: ignore
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecentReviewListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["analysis_reviews"],
        summary="최신 통합 리뷰 목록 조회 (메인용)",
        description="최신순으로 5개 가져오도록",
        responses={200: AnalysisReviewSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        recent_reviews = ReviewService.get_recent_reviews(limit=10)
        return Response(AnalysisReviewSerializer(recent_reviews, many=True).data)
