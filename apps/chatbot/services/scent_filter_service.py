from typing import Any

from apps.analysis.models import Scent

from ..prompts.support_context import (
    INTENSITY_RANGE,
    MOOD_TO_CATEGORY,
    MOOD_TO_TAGS,
    SPACE_TO_PLACE,
    TIME_TO_SEASON,
)
from .context_service import Context


def _scent_to_dict(scent: Scent) -> dict[str, Any]:
    recommended_places = scent.recommended_places or []
    if recommended_places and isinstance(recommended_places[0], dict):
        place_names = [p["name"] for p in recommended_places]
    else:
        place_names = recommended_places

    return {
        "id": scent.id,
        "name": scent.name,
        "englishName": scent.eng_name,  #
        "category": scent.categories,
        "intensity": scent.intensity,
        "tags": scent.tags or [],
        "season": scent.season or [],
        "recommendedPlaces": place_names,
        "isBestseller": scent.is_bestseller,
    }


def get_fallback_scents(excluded_ids: list[int] | None = None) -> list[dict[str, Any]]:
    qs = Scent.objects.filter(is_bestseller=True)
    if excluded_ids:
        qs = qs.exclude(id__in=excluded_ids)
    return [_scent_to_dict(s) for s in qs]


def filter_scents(ctx: Context, excluded_ids: list[int] | None = None) -> list[dict[str, Any]]:
    qs = Scent.objects.all()

    if excluded_ids:
        qs = qs.exclude(id__in=excluded_ids)

    space = ctx.get("space")
    mood = ctx.get("mood")
    intensity = ctx.get("intensity")
    time = ctx.get("time")

    candidates = [_scent_to_dict(s) for s in qs]

    if space:
        places = SPACE_TO_PLACE.get(space, [])
        candidates = [s for s in candidates if any(p in s["recommendedPlaces"] for p in places)]

    if mood:
        tags = MOOD_TO_TAGS.get(mood, [])
        categories = MOOD_TO_CATEGORY.get(mood, [])
        candidates = [s for s in candidates if any(t in s["tags"] for t in tags) or s["category"] in categories]

    if intensity:
        intensity_range = INTENSITY_RANGE.get(intensity)
        if intensity_range:
            min_val, max_val = intensity_range
            candidates = [s for s in candidates if min_val <= s["intensity"] <= max_val]

    if time:
        seasons = TIME_TO_SEASON.get(time, [])
        candidates = [s for s in candidates if any(season in s["season"] for season in seasons)]

    if not candidates:
        candidates = get_fallback_scents(excluded_ids)

    return candidates


def count_meaningful_turns(messages: list[dict[str, str]]) -> int:
    from .chatbot_completion_policy import is_meaningful_turn

    return sum(1 for msg in messages if msg["role"] == "user" and is_meaningful_turn(msg["content"]))
