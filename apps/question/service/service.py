import json
import math
import random
from typing import Any, cast

from django.core.cache import cache
from django.db.models import JSONField

from apps.analysis.models import Scent
from apps.core.utils.cloud_front import image_url_cloud
from apps.core.utils.s3_handler import S3Handler
from apps.question.models import Keyword, Question, QuestionsAnswer, QuestionsResults


class Service:
    _s3handler = S3Handler()

    @staticmethod
    def get_cached_data() -> tuple[dict[str, str], dict[str, int], dict[str, JSONField | Any]] | Any:
        cached_data = cache.get("scent_logic_maps")
        if cached_data is not None:
            return cached_data

        q_map = {q.content: q.category for q in Question.objects.all()}
        a_map = {a.answer: a.score for a in QuestionsAnswer.objects.all()}
        k_map = {k.name: k.score for k in Keyword.objects.all()}

        result = (q_map, a_map, k_map)

        cache.set("scent_logic_maps", result, 3600)

        return result

    @classmethod
    def match_score(cls, p1: dict[str, int], p2: dict[str, int]) -> int:
        d = cls.distance(p1, p2)
        max_dist = 223.606  # sqrt(5 * 100^2)
        score = (1 - (d / max_dist)) * 100
        return max(0, int(round(score)))

    @classmethod
    def build_user_profile(cls, survey_answers: list[dict[str, Any]]) -> dict[str, int]:
        cached_data = cls.get_cached_data()

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
            result = q.get("answer")

            if not isinstance(title, str) or not isinstance(result, str):
                continue

            key = q_map_data.get(title)
            score = a_map_data.get(result)

            if not key:
                continue

            if not score:
                continue

            if key and score is not None:
                profile[key].append(score)

        return {k: int(round(sum(v) / len(v))) if v else 50 for k, v in profile.items()}

    @classmethod
    def build_profile_from_keywords(cls, keywords: list[dict[str, Any]]) -> dict[str, int]:
        cached_data = cls.get_cached_data()

        q_map_data, a_map_data, k_map_data = cached_data

        profile = {
            "freshness": 50,
            "warmth": 50,
            "softness": 50,
            "depth": 50,
            "sweetness": 50,
        }

        for kw in keywords:
            name = kw.get("name")

            if not isinstance(name, str):
                continue

            boost = k_map_data.get(name)

            if not boost or not isinstance(boost, dict):
                continue

            for k, v in boost.items():
                profile[k] = max(0, min(100, profile[k] + v))

        return profile

    @staticmethod
    def distance(p1: dict[str, int], p2: dict[str, int]) -> float:
        return math.sqrt(sum((p1[k] - p2[k]) ** 2 for k in p1))

    @classmethod
    def find_best_scent(cls, user_profile: dict[str, int], scents: list[dict[str, Any]]) -> dict[str, Any]:
        sorted_scents = sorted(scents, key=lambda s: cls.distance(user_profile, s["profile"]))
        top3 = sorted_scents[:3]
        return random.choice(top3)

    @staticmethod
    def get_cached_scent_data() -> list[dict[str, Any]]:
        cached_scents = cache.get("scent_full_data")
        if cached_scents is not None:
            return cast(list[dict[str, Any]], cached_scents)

        scents = []
        for s in Scent.objects.all():
            scents.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "profile": s.profile,
                    "tags": s.tags,
                }
            )

        cache.set("scent_full_data", scents, 3600)
        return scents

    @classmethod
    def result_prompt(cls, combined_keywords: str, check_type: str) -> tuple[str, Any, int]:
        data = json.loads(combined_keywords)

        if check_type == "설문지":
            user_profile = cls.build_user_profile(data)
            add_text = ", ".join(
                f"{q.get('title')}: {q.get('answer')}"
                for q in data  # 많으면 10개 제한
            )
        else:
            user_profile = cls.build_profile_from_keywords(data)
            add_text = ", ".join(kw.get("name", "Unknown") for kw in data)

        selected_scent = cls.find_best_scent(user_profile, cls.get_cached_scent_data())

        match_score_data = cls.match_score(user_profile, selected_scent.get("profile", {}))

        scent_name = selected_scent.get("name")
        scent_profile = selected_scent.get("profile")
        scent_tags = selected_scent.get("tags")

        prompt = f"""
        user: {user_profile}
        preferences: {add_text}
        scent: {scent_name}, {scent_profile}, {scent_tags}
        match_score: {match_score_data}
    
        Explain why this perfume is recommended based on the user's preferences in a natural and 
        engaging way (3-5 sentences). Do not use Markdown, and translate the final answer into Korean so 
        that the output is only in Korean.
        """

        return prompt, selected_scent.get("id"), match_score_data

    @staticmethod
    def keyword_save(
        user_id: int, scent_id: int, answer_ai: str, json_data: str, division: str, match_score: int
    ) -> QuestionsResults:
        return QuestionsResults.objects.create(
            user_id=user_id,
            scent_id=scent_id,
            division=division,
            questions_json=json_data,
            answer_ai=answer_ai,
            match_score=match_score,
        )

    @classmethod
    def list_url(cls, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "name": place["name"],
                "description": place["description"],
                "imageUrl": image_url_cloud(place["imageUrl"]),
                "matchScore": place["matchScore"],
            }
            for place in data
        ]

    @classmethod
    def scent_edit(cls, scent_data: Scent) -> Scent:
        scent_data.thumbnail_url = image_url_cloud(scent_data.thumbnail_url) if scent_data.thumbnail_url else None

        scent_data.recommended_places = (
            cls.list_url(scent_data.recommended_places) if scent_data.recommended_places else None
        )
        return scent_data
