from typing import Any

from drf_spectacular.utils import OpenApiExample


def extend_schema(name: str, value: dict[str, Any], status_code: str) -> OpenApiExample:
    return OpenApiExample(
        name,
        value,
        status_codes=[status_code],
        response_only=True,
    )


def extend_schemas(name: str, value: list[dict[str, Any]], status_code: str) -> OpenApiExample:
    return OpenApiExample(
        name,
        value,
        status_codes=[status_code],
        response_only=True,
    )


value_list = {
    "200_question_get": extend_schemas(
        "Ok",
        [
            {
                "id": 1,
                "title": "질문 내용",
                "left_label": "상쾌한",
                "right_label": "포근한",
                "answer": [
                    {"content": "상쾌한"},
                    {"content": "약간 상쾌한"},
                    {"content": "약간 포근한"},
                    {"content": "포근한"},
                ],
            }
        ],
        "200",
    ),
    "201": extend_schema(
        "Created",
        {
            "id": 1,
            "recommended_scent": {
                "id": 14,
                "name": "레몬 리넨",
                "eng_name": "Lemon Linen",
                "description": "막 세탁한 리넨에 레몬 껍질의 산뜻함이 얹힌 듯한 향입니다. 깨끗하고 가벼운 분위기로 일상 공간을 환하게 정돈해 줍니다.",
                "categories": "citrus",
                "tags": ["깨끗한", "가벼운", "산뜻한", "정돈된"],
                "keywords": ["런드리", "햇볕", "기분전환"],
                "intensity": 52,
                "is_bestseller": "false",
                "scent_notes": {
                    "top": {
                        "items": ["레몬", "유자", "알데하이드"],
                        "title": "탑 노트",
                        "description": "청량하고 깨끗하게 퍼지는 향",
                    },
                    "base": {
                        "items": ["화이트 머스크", "시더우드", "앰버"],
                        "title": "베이스 노트",
                        "description": "깨끗함을 오래 남기는 향",
                    },
                    "middle": {
                        "items": ["린넨 어코드", "네롤리", "라벤더"],
                        "title": "미들 노트",
                        "description": "클린한 섬유감이 중심이 되는 향",
                    },
                },
                "profile": {"depth": 24, "warmth": 16, "softness": 58, "freshness": 88, "sweetness": 26},
                "season": ["spring", "summer"],
                "recommended_places": [
                    {
                        "name": "Laundry Room",
                        "imageUrl": "https://example.com/places/laundry-room-01.jpg",
                        "matchScore": 95,
                        "description": "섬유의 깨끗함과 잘 어울리는 공간",
                    },
                    {
                        "name": "Bedroom",
                        "imageUrl": "https://example.com/places/bedroom-08.jpg",
                        "matchScore": 91,
                        "description": "상쾌한 기분을 더하는 침실",
                    },
                    {
                        "name": "Entryway",
                        "imageUrl": "https://example.com/places/entryway-04.jpg",
                        "matchScore": 88,
                        "description": "반듯하고 깔끔한 인상을 주는 현관",
                    },
                ],
                "similar_scents": [13, 17, 20],
                "thumbnail_url": "",
                "created_at": "2026-04-15T05:41:54.846985Z",
            },
            "reason": "사용자님의 '산뜻한' 무드에 맞춰, '레몬 리넨'은 태그에 '산뜻한', '깨끗한', '가벼운'을 포함하고 있어 완벽하게 부합합니다. 특히, Freshness 수치가 88로 매우 높아 탁월한 상쾌함을 선사하며, Warmth와 Depth가 각각 16과 24로 낮아 가볍고 맑은 느낌을 더욱 강조합니다.",
        },
        "201",
    ),
    "200_list": extend_schemas(
        "OK",
        [
            {
                "id": 1,
                "recommended_scent": {
                    "id": 14,
                    "name": "레몬 리넨",
                    "eng_name": "Lemon Linen",
                    "thumbnail_url": "",
                },
                "created_at": "2026-04-15T05:41:54.846985Z",
            }
        ],
        "200",
    ),
    "200_review": extend_schema(
        "OK",
        {
            "id": 1,
            "recommended_scent": {
                "id": 14,
                "name": "레몬 리넨",
                "eng_name": "Lemon Linen",
                "description": "막 세탁한 리넨에 레몬 껍질의 산뜻함이 얹힌 듯한 향입니다. 깨끗하고 가벼운 분위기로 일상 공간을 환하게 정돈해 줍니다.",
                "categories": "citrus",
                "tags": ["깨끗한", "가벼운", "산뜻한", "정돈된"],
                "keywords": ["런드리", "햇볕", "기분전환"],
                "intensity": 52,
                "is_bestseller": "false",
                "scent_notes": {
                    "top": {
                        "items": ["레몬", "유자", "알데하이드"],
                        "title": "탑 노트",
                        "description": "청량하고 깨끗하게 퍼지는 향",
                    },
                    "base": {
                        "items": ["화이트 머스크", "시더우드", "앰버"],
                        "title": "베이스 노트",
                        "description": "깨끗함을 오래 남기는 향",
                    },
                    "middle": {
                        "items": ["린넨 어코드", "네롤리", "라벤더"],
                        "title": "미들 노트",
                        "description": "클린한 섬유감이 중심이 되는 향",
                    },
                },
                "profile": {"depth": 24, "warmth": 16, "softness": 58, "freshness": 88, "sweetness": 26},
                "season": ["spring", "summer"],
                "recommended_places": [
                    {
                        "name": "Laundry Room",
                        "imageUrl": "https://example.com/places/laundry-room-01.jpg",
                        "matchScore": 95,
                        "description": "섬유의 깨끗함과 잘 어울리는 공간",
                    },
                    {
                        "name": "Bedroom",
                        "imageUrl": "https://example.com/places/bedroom-08.jpg",
                        "matchScore": 91,
                        "description": "상쾌한 기분을 더하는 침실",
                    },
                    {
                        "name": "Entryway",
                        "imageUrl": "https://example.com/places/entryway-04.jpg",
                        "matchScore": 88,
                        "description": "반듯하고 깔끔한 인상을 주는 현관",
                    },
                ],
                "similar_scents": [13, 17, 20],
                "thumbnail_url": "",
                "created_at": "2026-04-15T05:41:54.846985Z",
            },
            "reason": "사용자님의 '산뜻한' 무드에 맞춰, '레몬 리넨'은 태그에 '산뜻한', '깨끗한', '가벼운'을 포함하고 있어 완벽하게 부합합니다. 특히, Freshness 수치가 88로 매우 높아 탁월한 상쾌함을 선사하며, Warmth와 Depth가 각각 16과 24로 낮아 가볍고 맑은 느낌을 더욱 강조합니다.",
            "review": "리뷰",
            "rating": 5,
        },
        "200",
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
    "200_keyword_get": extend_schemas(
        "OK", [{"keyword_id": 1, "keyword_division": "분위기", "keyword_name": "시원함"}], "200"
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
