from ..constants.mapping_keywords import (
    INTENSITY_MAPPING,
    MOOD_MAPPING,
    SPACE_MAPPING,
    TIME_MAPPING,
)

Context = dict[str, str | None]


def init_context() -> Context:
    return {
        "space": None,
        "mood": None,
        "intensity": None,
        "time": None,
    }


def rule_based_extract(text: str) -> Context:
    result = init_context()
    for keyword, value in SPACE_MAPPING.items():
        if keyword in text:
            result["space"] = value
            break
    for keyword, value in MOOD_MAPPING.items():
        if keyword in text:
            result["mood"] = value
            break
    for keyword, value in INTENSITY_MAPPING.items():
        if keyword in text:
            result["intensity"] = value
            break
    for keyword, value in TIME_MAPPING.items():
        if keyword in text:
            result["time"] = value
            break
    return result


def merge_context(existing: Context, new: Context) -> Context:
    return {key: new[key] if new.get(key) is not None else existing.get(key) for key in existing}


def context_score(ctx: Context) -> int:
    score = 0
    if ctx.get("space"):
        score += 2
    if ctx.get("mood"):
        score += 2
    if ctx.get("intensity"):
        score += 1
    if ctx.get("time"):
        score += 1
    return score


def can_recommend(ctx: Context) -> bool:
    if not ctx.get("space"):
        return False
    if not ctx.get("mood"):
        return False
    if not ctx.get("intensity") and not ctx.get("time"):
        return False
    return context_score(ctx) >= 5
