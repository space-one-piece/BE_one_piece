from typing import Any

from drf_spectacular.utils import OpenApiExample


def extend_schema(name: str, value: dict[str, Any], status_code: str) -> OpenApiExample:
    return OpenApiExample(
        name,
        value,
        status_codes=[status_code],
        response_only=True,
    )


value_list = {
    "200_question_get": extend_schema(
        "Ok", {"id": 1, "title": "질문 내용", "answer": [{"content": "상쾌한", "num": 1}]}, "200"
    ),
    "201": extend_schema(
        "Created",
        {
            "sent_id": 1,
            "scent_name": "자스민",
            "scent_categories": [{"category": "우디", "count": 12, "percentage": 50.0}],
            "scent_image_url": "https://aws/s3/images/question/jasmine.png",
            "scent_keywords": "#풍성한꽃향기",
            "scent_notes": {"top": "탑", "middle": "미들", "base": "베이스"},
            "description": "당신의 공간을 채워줍니다.",
            "question_image": "data:image/png;base64,iVBORw0KGg...",
        },
        "201",
    ),
    "200_web_get": extend_schema(
        "OK",
        {
            "sent_id": 1,
            "scent_name": "자스민",
            "scent_categories": [{"category": "우디", "count": 12, "percentage": 50.0}],
            "scent_image_url": "https://aws/s3/images/question/jasmine.png",
            "scent_keywords": "#풍성한꽃향기",
            "scent_notes": {"top": "탑", "middle": "미들", "base": "베이스"},
            "description": "당신의 공간을 채워줍니다.",
            "question_image": "data:image/png;base64,iVBORw0KGg...",
        },
        "200",
    ),
    "200_web_post": extend_schema("OK", {"web_share_url": "https://one_piece/api/v1/question/share/uuid"}, "200"),
    "200_keyword_get": extend_schema(
        "OK", {"keyword_id": 1, "keyword_division": "분위기", "keyword_name": "시원함"}, "200"
    ),
    "200": extend_schema("OK", {"message": "저장 되었습니다."}, "200"),
    "400_question": extend_schema("Bad Request", {"error_detail": {"results": ["Q1번 답변이 없습니다."]}}, "400"),
    "400_keyword": extend_schema(
        "Bad Request", {"error_detail": {"keyword_name": ["선택된 키워드가 없습니다."]}}, "400"
    ),
    "400": extend_schema("Bad Request", {"error_detail": "이미지가 없습니다."}, "400"),
    "401": extend_schema("Unauthorized", {"error_detail": "자격 인증 데이터가 제공되 않았습니다."}, "401"),
    "403": extend_schema("Forbidden", {"error_detail": "권한이 없습니다."}, "403"),
    "404": extend_schema("Not Found", {"error_detail": "질문 결과가 없습니다."}, "404"),
    "429": extend_schema("Too Mony Requests", {"error_detail": "너무 자주 접근하였습니다."}, "429"),
}
