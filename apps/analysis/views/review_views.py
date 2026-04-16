from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.review_serializers import AnalysisReviewSerializer
from ..service.review_service import ReviewService


class AnalysisReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis_review"],
        summary="특정 분석의 리뷰 조회",
        responses={
            200: AnalysisReviewSerializer,
            404: OpenApiResponse(description="분석 결과를 찾을 수 없음"),
        },
    )
    def get(self, request: Request, id: int) -> Response:
        review_data = ReviewService.get_review(analysis_id=id, user=request.user)  # type: ignore

        output_serializer = AnalysisReviewSerializer(review_data)

        return Response(output_serializer.data)

    @extend_schema(
        tags=["image_analysis_review"],
        summary="분석 결과에 대한 리뷰 작성/수정",
        description="""
        - 최초 작성 시: `review`와 `rating` 둘 다 필수
        - 수정 시: 두 필드 중 하나만 보내도 수정 가능
        """,
        request=AnalysisReviewSerializer,
        responses={
            200: OpenApiResponse(description="리뷰 저장 성공"),
            400: OpenApiResponse(description="잘못된 입력값"),
        },
    )
    def patch(self, request: Request, id: int) -> Response:
        input_serializer = AnalysisReviewSerializer(data=request.data, partial=True)
        input_serializer.is_valid(raise_exception=True)

        updated_analysis = ReviewService.patch_review(
            analysis_id=id,
            user=request.user,  # type: ignore
            data=input_serializer.validated_data,
        )

        output_serializer = AnalysisReviewSerializer(updated_analysis)

        return Response(output_serializer.data)

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
        ReviewService.delete_review(analysis_id=id, user=request.user)  # type: ignore

        return Response(status=status.HTTP_204_NO_CONTENT)


class MyReviewListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis_review"],
        summary="내 리뷰 전체 목록",
        description="내 리뷰 전체 목록",
        responses={
            200: AnalysisReviewSerializer(many=True),
        },
    )
    def get(self, request: Request) -> Response:
        user_id = request.user.id
        review_list = ReviewService.get_my_reviews(user_id=user_id)
        output_serializer = AnalysisReviewSerializer(review_list, many=True)

        return Response(output_serializer.data)
