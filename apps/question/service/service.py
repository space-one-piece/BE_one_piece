import json
import logging
import math
import random
from typing import Any, cast
from urllib.parse import urlparse

from botocore.exceptions import ClientError
from django.core.cache import cache

from apps.core.utils.s3_handler import S3Handler
from apps.question.models import Keyword, Question, QuestionsAnswer, QuestionsResults

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


ANSWER_SCORE = {
    0: 0,
    1: 33,
    2: 66,
    3: 100,
}


def get_cached_data():
    cached_data = cache.get("scent_logic_maps")
    if cached_data is not None:
        return cached_data

    q_map = {q.content: q.category for q in Question.objects.all()}
    a_map = {a.answer: a.score for a in QuestionsAnswer.objects.all()}
    k_map = {k.name: k.score for k in Keyword.objects.all()}

    result = (q_map, a_map, k_map)

    cache.set("scent_logic_maps", result, 3600)

    return result


def build_user_profile(survey_answers: list[dict[str, Any]]) -> dict[str, int]:
    cached_data = get_cached_data()

    q_map_data, a_map_data, k_map_data = cached_data

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

        key = q_map_data.get(title)
        if not key:
            continue

        if not result or not isinstance(result, str):
            continue

        score = a_map_data.get(result)
        if score is None:
            continue

        profile[key].append(score)

    return {k: int(sum(v) / len(v)) if v else 50 for k, v in profile.items()}


def build_profile_from_keywords(keywords: list[dict[str, Any]]) -> dict[str, int]:
    cached_data = get_cached_data()

    q_map_data, a_map_data, k_map_data = cached_data

    profile = {
        "freshness": 50,
        "warmth": 50,
        "softness": 50,
        "depth": 50,
        "sweetness": 50,
    }

    for kw in keywords:
        name = kw.get("fields", {}).get("name")

        boost = k_map_data.get(name)
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
