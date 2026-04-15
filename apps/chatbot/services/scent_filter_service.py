from typing import Any

from ..prompts.support_context import (
    INTENSITY_RANGE,
    MOOD_TO_CATEGORY,
    MOOD_TO_TAGS,
    SCENT_DATA,
    SPACE_TO_PLACE,
    TIME_TO_SEASON,
)
from .context_service import Context


def get_fallback_scents(excluded_ids: list[int] | None = None) -> list[dict[str, Any]]:
    candidates = [s for s in SCENT_DATA if s["isBestseller"]]
    if excluded_ids:
        candidates = [s for s in candidates if s["id"] not in excluded_ids]
    return candidates


def filter_scents(ctx: Context, excluded_ids: list[int] | None = None) -> list[dict[str, Any]]:
    candidates = SCENT_DATA.copy()

    if excluded_ids:
        candidates = [s for s in candidates if s["id"] not in excluded_ids]

    space = ctx.get("space")
    if space:
        places = SPACE_TO_PLACE.get(space, [])
        candidates = [s for s in candidates if any(p in s["recommendedPlaces"] for p in places)]

    mood = ctx.get("mood")
    if mood:
        tags = MOOD_TO_TAGS.get(mood, [])
        categories = MOOD_TO_CATEGORY.get(mood, [])
        candidates = [s for s in candidates if any(t in s["tags"] for t in tags) or s["category"] in categories]

    intensity = ctx.get("intensity")
    if intensity:
        intensity_range = INTENSITY_RANGE.get(intensity)
        if intensity_range:
            min_val, max_val = intensity_range
            candidates = [s for s in candidates if min_val <= s["intensity"] <= max_val]

    time = ctx.get("time")
    if time:
        seasons = TIME_TO_SEASON.get(time, [])
        candidates = [s for s in candidates if any(season in s["season"] for season in seasons)]

    if not candidates:
        candidates = get_fallback_scents(excluded_ids)

    return candidates


def count_meaningful_turns(messages: list[dict[str, str]]) -> int:
    from .chatbot_completion_policy import is_meaningful_turn

    return sum(1 for msg in messages if msg["role"] == "user" and is_meaningful_turn(msg["content"]))
