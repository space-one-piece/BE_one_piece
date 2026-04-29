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
                "id": 5,
                "name": "체리 베일",
                "eng_name": "Cherry Veil",
                "description": "은은한 과실감과 꽃잎의 부드러움이 함께 감도는 향입니다. 발랄함보다는 섬세하고 여린 인상에 가까워 작은 공간에 잘 어울립니다.",
                "categories": "floral",
                "tags": ["달콤한", "사랑스러운", "섬세한", "은은한"],
                "keywords": ["소녀감성", "여리여리", "달콤함"],
                "intensity": 62,
                "is_bestseller": "false",
                "scent_notes": {
                    "top": {
                        "items": ["체리", "레드 베리", "베르가못"],
                        "title": "탑 노트",
                        "description": "가볍게 퍼지는 달콤한 시작",
                    },
                    "base": {
                        "items": ["머스크", "샌달우드", "바닐라"],
                        "title": "베이스 노트",
                        "description": "달콤함을 잡아주는 잔향",
                    },
                    "middle": {
                        "items": ["체리블라썸", "로즈", "바이올렛"],
                        "title": "미들 노트",
                        "description": "부드러운 꽃향으로 이어지는 중심",
                    },
                },
                "profile": {"depth": 53, "warmth": 42, "softness": 69, "freshness": 47, "sweetness": 63},
                "season": ["spring", "autumn"],
                "recommended_places": [
                    {
                        "name": "Bedroom",
                        "description": "포근하고 아늑한 분위기를 완성하는 침실",
                        "imageUrl": "https://cloudfront.net/uploads/images/place/bedroom.jpg",
                        "matchScore": 95,
                    },
                    {
                        "name": "Vanity",
                        "description": "개인적인 무드를 완성하는 공간",
                        "imageUrl": "https://cloudfront.net/uploads/images/place/vanity.jpg",
                        "matchScore": 91,
                    },
                    {
                        "name": "Dressing Room",
                        "description": "섬세한 무드를 더해주는 드레스룸",
                        "imageUrl": "https://cloudfront.net/uploads/images/place/dressing-room.jpg",
                        "matchScore": 87,
                    },
                    {
                        "name": "Living Room",
                        "description": "편안한 일상이 머무는 거실",
                        "imageUrl": "https://cloudfront.net/uploads/images/place/living-room.jpg",
                        "matchScore": 83,
                    },
                ],
                "similar_scents": [
                    {
                        "id": 2,
                        "name": "로즈 미스트",
                        "categories": "floral",
                        "tags": ["우아한", "잔잔한", "플로럴", "정돈된"],
                        "description": "이슬 맺힌 장미 정원을 떠올리게 하는 향입니다. 우아하고 차분한 플로럴 톤이 공간을 정돈된 분위기로 채워 줍니다.",
                        "eng_name": "Rose Mist",
                        "intensity": 64,
                        "season": ["spring", "summer"],
                        "thumbnail_url": "https://cloudfront.net/uploads/images/scent/rose-mist.jpg",
                    },
                    {
                        "id": 1,
                        "name": "블라썸 드림",
                        "categories": "floral",
                        "tags": ["따뜻한", "부드러운", "달콤한", "로맨틱"],
                        "description": "체리 블라썸과 머스크, 바닐라가 부드럽게 어우러진 향입니다. 사랑스럽고 포근한 분위기를 더해 주며, 공간 안에 로맨틱한 여운을 남깁니다.",
                        "eng_name": "Blossom Dream",
                        "intensity": 76,
                        "season": ["spring", "autumn"],
                        "thumbnail_url": "https://cloudfront.net/uploads/images/scent/blossom-dream.jpg",
                    },
                    {
                        "id": 3,
                        "name": "화이트 피오니",
                        "categories": "floral",
                        "tags": ["맑은", "가벼운", "산뜻한", "깨끗한"],
                        "description": "깨끗한 화이트 페탈의 느낌을 담은 플로럴 향입니다. 가볍고 맑은 분위기가 공간에 부드럽게 스며들어 산뜻한 인상을 남깁니다.",
                        "eng_name": "White Peony",
                        "intensity": 58,
                        "season": ["spring", "summer"],
                        "thumbnail_url": "https://cloudfront.net/uploads/images/scent/white-peony.jpg",
                    },
                    {
                        "id": 29,
                        "name": "페어 벨벳",
                        "categories": "fruity",
                        "tags": ["사랑스러운", "밝은", "과즙감 있는", "부드러운"],
                        "description": "잘 익은 배의 은은한 과즙감과 부드러운 머스크가 만나 밝고 사랑스러운 무드를 연출하는 향입니다. 과하지 않게 기분을 환하게 바꿔 줍니다.",
                        "eng_name": "Pear Velvet",
                        "intensity": 60,
                        "season": ["spring", "summer"],
                        "thumbnail_url": "https://cloudfront.net/uploads/images/scent/pear-velvet.jpg",
                    },
                ],
                "thumbnail_url": "https://cloudfront.net/uploads/images/scent/cherry-veil.jpg",
                "created_at": "2026-04-23T06:09:23.850859Z",
            },
            "ai_comment": "체리 베일은 고객님의 특별한 취향에 90점이라는 높은 점수로 완벽하게 어울리는 향수입니다. 69점의 부드러움과 63점의 달콤함이 조화롭게 어우러져 안락한 침실에 꼭 맞는 포근하고 사랑스러운 분위기를 선사할 거예요. 53점의 은은한 깊이감과 따뜻한 잔향은 편안함을 더해주고, '달콤한', '사랑스러운', '섬세한'이라는 키워드처럼 화사한 거실에서도 부담 없이 기분 좋은 향기로 공간을 채워줄 것입니다. 이 향수는 포근함과 동시에 집안에 화사함을 더하고 싶어하는 고객님의 취향을 아름답게 만족시켜 드릴 겁니다.",
            "match_score": 90,
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
                "id": 5,
                "name": "체리 베일",
                "eng_name": "Cherry Veil",
                "description": "은은한 과실감과 꽃잎의 부드러움이 함께 감도는 향입니다. 발랄함보다는 섬세하고 여린 인상에 가까워 작은 공간에 잘 어울립니다.",
                "categories": "floral",
                "tags": ["달콤한", "사랑스러운", "섬세한", "은은한"],
                "keywords": ["소녀감성", "여리여리", "달콤함"],
                "intensity": 62,
                "is_bestseller": "false",
                "scent_notes": {
                    "top": {
                        "items": ["체리", "레드 베리", "베르가못"],
                        "title": "탑 노트",
                        "description": "가볍게 퍼지는 달콤한 시작",
                    },
                    "base": {
                        "items": ["머스크", "샌달우드", "바닐라"],
                        "title": "베이스 노트",
                        "description": "달콤함을 잡아주는 잔향",
                    },
                    "middle": {
                        "items": ["체리블라썸", "로즈", "바이올렛"],
                        "title": "미들 노트",
                        "description": "부드러운 꽃향으로 이어지는 중심",
                    },
                },
                "profile": {"depth": 53, "warmth": 42, "softness": 69, "freshness": 47, "sweetness": 63},
                "season": ["spring", "autumn"],
                "recommended_places": [
                    {
                        "name": "Bedroom",
                        "description": "포근하고 아늑한 분위기를 완성하는 침실",
                        "imageUrl": "https://cloudfront.net/uploads/images/place/bedroom.jpg",
                        "matchScore": 95,
                    },
                    {
                        "name": "Vanity",
                        "description": "개인적인 무드를 완성하는 공간",
                        "imageUrl": "https://cloudfront.net/uploads/images/place/vanity.jpg",
                        "matchScore": 91,
                    },
                    {
                        "name": "Dressing Room",
                        "description": "섬세한 무드를 더해주는 드레스룸",
                        "imageUrl": "https://cloudfront.net/uploads/images/place/dressing-room.jpg",
                        "matchScore": 87,
                    },
                    {
                        "name": "Living Room",
                        "description": "편안한 일상이 머무는 거실",
                        "imageUrl": "https://cloudfront.net/uploads/images/place/living-room.jpg",
                        "matchScore": 83,
                    },
                ],
                "similar_scents": [
                    {
                        "id": 2,
                        "name": "로즈 미스트",
                        "categories": "floral",
                        "tags": ["우아한", "잔잔한", "플로럴", "정돈된"],
                        "description": "이슬 맺힌 장미 정원을 떠올리게 하는 향입니다. 우아하고 차분한 플로럴 톤이 공간을 정돈된 분위기로 채워 줍니다.",
                        "eng_name": "Rose Mist",
                        "intensity": 64,
                        "season": ["spring", "summer"],
                        "thumbnail_url": "https://cloudfront.net/uploads/images/scent/rose-mist.jpg",
                    },
                    {
                        "id": 1,
                        "name": "블라썸 드림",
                        "categories": "floral",
                        "tags": ["따뜻한", "부드러운", "달콤한", "로맨틱"],
                        "description": "체리 블라썸과 머스크, 바닐라가 부드럽게 어우러진 향입니다. 사랑스럽고 포근한 분위기를 더해 주며, 공간 안에 로맨틱한 여운을 남깁니다.",
                        "eng_name": "Blossom Dream",
                        "intensity": 76,
                        "season": ["spring", "autumn"],
                        "thumbnail_url": "https://cloudfront.net/uploads/images/scent/blossom-dream.jpg",
                    },
                    {
                        "id": 3,
                        "name": "화이트 피오니",
                        "categories": "floral",
                        "tags": ["맑은", "가벼운", "산뜻한", "깨끗한"],
                        "description": "깨끗한 화이트 페탈의 느낌을 담은 플로럴 향입니다. 가볍고 맑은 분위기가 공간에 부드럽게 스며들어 산뜻한 인상을 남깁니다.",
                        "eng_name": "White Peony",
                        "intensity": 58,
                        "season": ["spring", "summer"],
                        "thumbnail_url": "https://cloudfront.net/uploads/images/scent/white-peony.jpg",
                    },
                    {
                        "id": 29,
                        "name": "페어 벨벳",
                        "categories": "fruity",
                        "tags": ["사랑스러운", "밝은", "과즙감 있는", "부드러운"],
                        "description": "잘 익은 배의 은은한 과즙감과 부드러운 머스크가 만나 밝고 사랑스러운 무드를 연출하는 향입니다. 과하지 않게 기분을 환하게 바꿔 줍니다.",
                        "eng_name": "Pear Velvet",
                        "intensity": 60,
                        "season": ["spring", "summer"],
                        "thumbnail_url": "https://cloudfront.net/uploads/images/scent/pear-velvet.jpg",
                    },
                ],
                "thumbnail_url": "https://cloudfront.net/uploads/images/scent/cherry-veil.jpg",
                "created_at": "2026-04-23T06:09:23.850859Z",
            },
            "ai_comment": "체리 베일은 고객님의 특별한 취향에 90점이라는 높은 점수로 완벽하게 어울리는 향수입니다. 69점의 부드러움과 63점의 달콤함이 조화롭게 어우러져 안락한 침실에 꼭 맞는 포근하고 사랑스러운 분위기를 선사할 거예요. 53점의 은은한 깊이감과 따뜻한 잔향은 편안함을 더해주고, '달콤한', '사랑스러운', '섬세한'이라는 키워드처럼 화사한 거실에서도 부담 없이 기분 좋은 향기로 공간을 채워줄 것입니다. 이 향수는 포근함과 동시에 집안에 화사함을 더하고 싶어하는 고객님의 취향을 아름답게 만족시켜 드릴 겁니다.",
            "match_score": 90,
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
    "200_web_image": extend_schema("OK", {"image_data": "d2lb...."}, "200"),
    "400": extend_schema("Bad Request", {"error_detail": "이미지가 없습니다."}, "400"),
    "401": extend_schema("Unauthorized", {"error_detail": "자격 인증 데이터가 제공되 않았습니다."}, "401"),
    "403": extend_schema("Forbidden", {"error_detail": "권한이 없습니다."}, "403"),
    "404": extend_schema("Not Found", {"error_detail": "질문 결과가 없습니다."}, "404"),
    "429": extend_schema("Too Many Requests", {"error_detail": "너무 자주 접근하였습니다."}, "429"),
}
