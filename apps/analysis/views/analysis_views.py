from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.serializers.analysis_serializers import (
    AnalysisCreateSerializer,
    AnalysisDetailSerializer,
    AnalysisListSerializer,
    IntegratedFeedbackSerializer,
)
from apps.analysis.service.analysis_service import AnalysisService
from apps.core.paginations import StandardCustomPagination
from apps.core.serializers.presigned_url_serializer import PresignedUrlRequestSerializer


# 이미지 프리사인 URL 요청
class UploadURLAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis"],
        summary="S3 프리사인 URL 발급 요청",
        description="프론트엔드에서 S3에 직접 이미지를 업로드하기 위한 프리사인 URL을 발급합니다.",
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(description="발급 성공"),
            400: OpenApiResponse(description="잘못된 파일 형식/이름"),
            401: OpenApiResponse(description="로그인 에러"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = PresignedUrlRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AnalysisService.create_upload_resource(
            user=request.user,  # type: ignore
            file_name=serializer.validated_data["file_name"],
        )

        return Response(result)


# 이미지 분석 / 리스트
class AnalysisListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        queryset = AnalysisService.get_analysis_list(user_id=request.user.id)

        paginator = StandardCustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        output_serializer = AnalysisListSerializer(paginated_queryset, many=True)
        # return paginator.get_paginated_response(output_serializer.data)
        return Response(output_serializer.data)

    @extend_schema(
        tags=["image_analysis"],
        summary="이미지 분석 시작",
        description="S3에 업로드된 이미지 키를 전달받아 분석",
        request=AnalysisCreateSerializer,
        responses={
            201: AnalysisDetailSerializer,
            400: OpenApiResponse(description="필수값 누락"),
            404: OpenApiResponse(description="필수값 이상"),
            429: OpenApiResponse(description="호출횟수 초과"),
            503: OpenApiResponse(description="서버이상"),
        },
    )
    def post(self, request: Request) -> Response:
        input_serializer = AnalysisCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        image_key = input_serializer.validated_data["image_key"]
        try:
            analysis_record, _ = AnalysisService.image_analysis_process(user=request.user, img_key=image_key)  # type: ignore
        except ValueError as e:
            raise ValidationError(detail=str(e))

        output_serializer = AnalysisDetailSerializer(analysis_record)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


# 이미지 분석 상세 조회
class AnalysisDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, id: int) -> Response:
        data = AnalysisService.get_my_analysis(user_id=request.user.id, analysis_id=id)

        if not data:
            raise NotFound(detail="접근권한이 없거나 존재하지 않는 분석 데이터")

        output_serializer = AnalysisDetailSerializer(data)
        return Response(output_serializer.data)

    @extend_schema(
        tags=["image_analysis"],
        summary="특정 분석 결과 삭제",
        responses={
            204: OpenApiResponse(description="삭제 성공 (본문 없음)"),
            404: OpenApiResponse(description="존재하지 않는 분석 데이터"),
            500: OpenApiResponse(description="서버통신 오류"),
        },
    )
    def delete(self, request: Request, id: int) -> Response:
        success = AnalysisService.delete_analysis(user_id=request.user.id, analysis_id=id)

        if not success:
            raise NotFound(detail="삭제할 분석 결과가 없거나 접근 권한이 없습니다.")

        return Response(status=status.HTTP_204_NO_CONTENT)


# 분석 결과 저장
class AnalysisFeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["analysis_intergration"],
        summary="분석결과 내 향기 저장",
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                required=False,
                description="분석 타입 (image, chatbot, keyword, survey). 기본값: image",
            )
        ],
        request=inline_serializer(
            name="FeedbackInput",
            fields={"status": serializers.BooleanField(help_text="도움/저장 여부 (true/false)")},
        ),
        responses={
            200: OpenApiResponse(description="분석 저장 성공"),
            400: OpenApiResponse(description="필수값 이상"),
            404: OpenApiResponse(description="분석이 존재하지 않음"),
        },
    )
    def patch(self, request: Request, id: int) -> Response:
        analysis_type = request.query_params.get("type", "image")
        valid_types = {"image", "chatbot", "keyword", "survey"}

        if analysis_type not in valid_types:
            raise ValidationError({"detail": f"유효하지 않은 type. 허용값: {valid_types}"})

        status_val = request.data.get("status")

        if status_val is None:
            raise ValidationError({"detail": "status 필드는 필수입니다. (true/false)"})
        if not isinstance(status_val, bool):
            raise ValidationError({"detail": "status는 boolean 타입이어야 합니다."})

        updated_analysis = AnalysisService.update_analysis_feedback(
            user_id=request.user.id, analysis_id=id, analysis_type=analysis_type, status=status_val
        )

        if not updated_analysis:
            raise NotFound(detail=f"해당 {analysis_type} 분석 결과를 찾을 수 없거나 접근 권한이 없습니다.")

        return Response({"detail": "피드백이 성공적으로 반영되었습니다."}, status=status.HTTP_200_OK)


# 분석결과 저장한 리스트 반환
class AnalysisFeedbackListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["analysis_intergration"],
        summary="내가 저장한 컬렉션 조회",
        description="분석/추천 결과를 최신순으로 가져옵니다.",
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                required=False,
                description="특정 타입만 필터링 (image, chatbot, keyword, survey). 없으면 전체 반환",
            )
        ],
        responses={
            200: OpenApiResponse(description="성공"),
        },
    )
    def get(self, request: Request) -> Response:
        analysis_type = request.query_params.get("type")
        valid_types = {"image", "chatbot", "keyword", "survey"}

        if analysis_type and analysis_type not in valid_types:
            raise ValidationError({"detail": f"유효하지 않은 type. 허용값: {valid_types}"})

        feedback_list = AnalysisService.get_integrated_feedback_list(
            user_id=request.user.id, analysis_type=analysis_type
        )

        paginator = StandardCustomPagination()
        paginated_queryset = paginator.paginate_queryset(feedback_list, request, view=self)  # type: ignore

        output_serializer = IntegratedFeedbackSerializer(paginated_queryset, many=True)
        # return paginator.get_paginated_response(output_serializer.data)
        return Response(output_serializer.data)


# 유저 분석 통계 반환
class AnalysisStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis"],
        summary="유저의 전반적인 분석 통계 조회",
        responses={
            200: OpenApiResponse(description="통계 데이터 반환 성공"),
        },
    )
    def get(self, request: Request) -> Response:
        stats_data = AnalysisService.get_user_statistics(user_id=request.user.id)

        return Response({"data": stats_data})


# 통합 분석 결과 리스트
class IntegratedHistoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["analysis_intergration"],
        summary="유저의 분석/추천 결과 통합 리스트",
        responses={
            200: OpenApiResponse(description="성공"),
        },
    )
    def get(self, request: Request) -> Response:
        history_list = AnalysisService.get_integrated_history_list(user_id=request.user.id)

        paginator = StandardCustomPagination()
        paginated_queryset = paginator.paginate_queryset(history_list, request, view=self)  # type: ignore

        output_serializer = AnalysisListSerializer(paginated_queryset, many=True)
        # return paginator.get_paginated_response(output_serializer.data)
        return Response(output_serializer.data)


# 분석 통합 결과 상세조회
class AnalysisTotalDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["analysis_intergration"],
        summary="통합 분석 결과 상세 조회",
        description="ID와 Type을 받아 이미지/챗봇/키워드 중 적절한 분석 결과를 반환합니다.",
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                required=True,
                description="분석 타입 (허용값: image, chatbot, keyword, survey)",
            )
        ],
    )
    def get(self, request: Request, id: int) -> Response:
        analysis_type = request.query_params.get("type")
        value_type = {"image", "chatbot", "keyword", "survey"}

        if not analysis_type:
            raise ValidationError({"detail": "type 파라미터가 필요합니다. (image, chatbot, keyword, survey)"})

        if analysis_type not in value_type:
            raise ValidationError({"detail": f"유효하지 않은 type. 허용값: {value_type}"})

        instance, output_serializer = AnalysisService.get_total_detail(
            user_id=request.user.id, analysis_id=id, analysis_type=analysis_type
        )

        if not instance:
            raise NotFound(detail=f"해당 {analysis_type} 분석 결과를 찾을 수 없습니다.")

        serializer = output_serializer(instance)
        return Response(serializer.data)
