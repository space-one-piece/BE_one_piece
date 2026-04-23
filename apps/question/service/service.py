import json
import logging
import math
import random
from typing import Any, cast
from urllib.parse import urlparse

from botocore.exceptions import ClientError

from apps.core.utils.s3_handler import S3Handler
from apps.question.models import QuestionsResults

s3handler = S3Handler()


def image_url_edit(image_url: str) -> str:
    parsed = urlparse(image_url)
    return parsed.path.lstrip("/") if parsed is not None else image_url


def s3_image(image_url: str) -> str | None:
    if image_url is not None:
        image_key = image_url_edit(image_url)
        try:
            return s3handler.generate_get_presigned_url(image_key)
        except ClientError as e:
            logger = logging.getLogger(__name__)
            logger.error(e)
            return image_url

    return None


def parse_gemini_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        cleaned = cleaned.replace("json\n", "", 1)

    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]

    cleaned = cleaned.strip()

    return cast(dict[str, Any], json.loads(cleaned))


QUESTION_MAPPING = {
    "아침에 선호하는 향": "freshness",
    "업무 중 선호하는 향": "depth",
    "휴식 시 선호하는 향": "softness",
    "비 오는 날의 향": "freshness",
    "잠들기 전의 향": "softness",
    "첫 데이트의 향": "sweetness",
    "겨울날 벽난로의 향": "warmth",
    "햇살 가득한 오후의 향": "freshness",
    "숲속 산책의 향": "freshness",
    "세탁 직후의 향": "freshness",
    "여행지에서의 향": "freshness",
    "우울할 때 위로가 되는 향": "softness",
    "자신감을 주는 향": "depth",
    "봄날 꽃시장의 향": "sweetness",
    "가을 낙엽의 향": "depth",
    "여름 바다의 향": "freshness",
    "오래된 책방의 향": "depth",
    "달콤한 디저트의 향": "sweetness",
    "갓 깎은 풀의 향": "freshness",
    "도시의 세련된 향": "depth",
    "새벽 공기의 향": "freshness",
    "집안 거실의 향": "softness",
    "운동 후의 향": "freshness",
    "명상할 때의 향": "depth",
    "부드러운 캐시미어의 향": "softness",
    "쌉싸름한 차(Tea)의 향": "warmth",
    "빈티지한 가죽의 향": "depth",
    "밤바다 산책의 향": "depth",
    "상큼한 시트러스의 향": "freshness",
    "나만의 시그니처 향": "depth",
}

ANSWER_TEXT_SCORE = {
    "상쾌한": 0,
    "약간 상쾌한": 33,
    "약간 포근한": 66,
    "포근한": 100,
    "가벼운": 0,
    "약간 가벼운": 33,
    "약간 깊은": 66,
    "깊은": 100,
    "쌉쌀한": 0,
    "약간 쌉쌀한": 33,
    "약간 고소한": 66,
    "고소한": 100,
    "톡 쏘는": 0,
    "약간 톡 쏘는": 33,
    "약간 달콤상콤한": 66,
    "달콤상콤한": 100,
    "맑은": 0,
    "약간 맑은": 33,
    "약간 안락한": 66,
    "안락한": 100,
    "광활한": 0,
    "약간 광활한": 33,
    "약간 비밀스러운": 66,
    "비밀스러운": 100,
    "생기있는": 0,
    "약간 생기있는": 33,
    "약간 여유로운": 66,
    "여유로운": 100,
    "투명한": 0,
    "약간 투명한": 33,
    "약간 고요한": 66,
    "고요한": 100,
    "정갈한": 0,
    "약간 정갈한": 33,
    "약간 오래된": 66,
    "오래된": 100,
    "강렬한": 0,
    "약간 강렬한": 33,
    "약간 은근한": 66,
    "은근한": 100,
}

ANSWER_SCORE = {
    0: 0,
    1: 33,
    2: 66,
    3: 100,
}

KEYWORD_PROFILE_MAP = {
    "안락한 침실": {"softness": +20, "warmth": +10},
    "화사한 거실": {"sweetness": +15, "freshness": +10},
    "집중의 서재": {"depth": +15},
    "청결한 욕실/현관": {"freshness": +20},
    "프라이빗 드레스룸": {"depth": +10, "softness": +10},
    "미니멀 & 정제된": {"freshness": +15},
    "우아함 & 고급스러운": {"depth": +15, "sweetness": +10},
    "로맨틱 & 달콤한": {"sweetness": +20},
    "내추럴 & 안정적인": {"softness": +15, "freshness": +10},
    "볼드 & 강렬한": {"depth": +20},
    "보송한 리넨": {"softness": +15, "freshness": +10},
    "매끄러운 벨벳": {"softness": +20, "depth": +10},
    "드라이한 나무": {"depth": +20, "warmth": +10},
    "촉촉한 이슬": {"freshness": +20},
    "포근한 캐시미어": {"softness": +25, "warmth": +10},
    "눈부신 아침": {"freshness": +20},
    "고요한 저녁": {"depth": +15, "softness": +10},
    "싱그러운 봄/여름": {"freshness": +20, "sweetness": +10},
    "깊어지는 가을/겨울": {"depth": +20, "warmth": +10},
    "비 온 뒤": {"freshness": +15, "depth": +10},
    "시트러스 (상쾌함)": {"freshness": +25},
    "우디 (묵직함)": {"depth": +25, "warmth": +10},
    "플로럴 (화사함)": {"sweetness": +20, "softness": +10},
    "머스크 (포근함)": {"softness": +25, "warmth": +10},
    "허벌 & 스파이시 (개성)": {"depth": +15, "freshness": +10},
}


def build_user_profile(survey_answers: list[dict[str, Any]]) -> dict[str, int]:
    profile: dict[str, list[int]] = {
        "freshness": [],
        "warmth": [],
        "softness": [],
        "depth": [],
        "sweetness": [],
    }

    for q in survey_answers:
        title = q.get("title")
        result = q.get("results")

        if not title or not isinstance(title, str):
            continue

        key = QUESTION_MAPPING.get(title)
        if not key:
            continue

        if not result or not isinstance(result, str):
            continue

        score = ANSWER_TEXT_SCORE.get(result)
        if score is None:
            continue

        profile[key].append(score)

    return {k: int(sum(v) / len(v)) if v else 50 for k, v in profile.items()}


def build_profile_from_keywords(keywords: list[dict[str, Any]]) -> dict[str, int]:
    profile = {
        "freshness": 50,
        "warmth": 50,
        "softness": 50,
        "depth": 50,
        "sweetness": 50,
    }

    for kw in keywords:
        name = kw.get("fields", {}).get("name")

        boost = KEYWORD_PROFILE_MAP.get(name)
        if not boost:
            continue

        for k, v in boost.items():
            profile[k] = max(0, min(100, profile[k] + v))

    return profile


def distance(p1: dict[str, int], p2: dict[str, int]) -> float:
    return math.sqrt(sum((p1[k] - p2[k]) ** 2 for k in p1))


def find_best_scent(user_profile: dict[str, int], scents: list[dict[str, Any]]) -> dict[str, Any]:
    sorted_scents = sorted(scents, key=lambda s: distance(user_profile, s["profile"]))
    top3 = sorted_scents[:3]
    return random.choice(top3)


def result_prompt(combined_keywords: str, check_type: str) -> tuple[str, Any]:
    from apps.analysis.models import Scent

    data = json.loads(combined_keywords)

    if check_type == "설문지":
        user_profile = build_user_profile(data)
        add_text = ", ".join(f"{q.get('title')}: {q.get('answer')}" for q in data)
    else:
        user_profile = build_profile_from_keywords(data)
        add_text = ", ".join(kw.get("name") for kw in data)

    # SCENT_DATA → DB 조회로 변경
    scent_data = cast(
        list[dict[str, Any]],
        list(
            Scent.objects.values(
                "id",
                "name",
                "categories",
                "tags",
                "intensity",
                "season",
                "recommended_places",
                "is_bestseller",
                "profile",
            )
        ),
    )
    selected_scent = find_best_scent(user_profile, scent_data)

    scent_name = selected_scent.get("name")
    scent_profile = selected_scent.get("profile")
    scent_tags = selected_scent.get("tags")

    prompt = f"""
    user: {user_profile}
    preferences: {add_text}
    scent: {scent_name}, {scent_profile}, {scent_tags}

    Explain why this perfume is recommended based on the user's preferences in a natural and 
    engaging way (3-5 sentences). Do not use Markdown, and translate the final answer into Korean so 
    that the output is only in Korean.
    """

    return prompt, selected_scent.get("id")


def keyword_save(user_id: int, scent_id: int, answer_ai: str, json_data: str, division: str) -> QuestionsResults:
    return QuestionsResults.objects.create(
        user_id=user_id, scent_id=scent_id, division=division, questions_json=json_data, answer_ai=answer_ai
    )
