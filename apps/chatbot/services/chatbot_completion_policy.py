import re

from rest_framework.exceptions import ValidationError

from ..constants.blocked_keywords import (
    BLOCKED_NONSENSE_KEYWORDS,
    BLOCKED_PROFANITY_KEYWORDS,
    BLOCKED_PROMPT_KEYWORDS,
)

MAX_INPUT_LENGTH = 500
MAX_TOTAL_TURNS = 5
MAX_MEANINGFUL_TURNS = 3

_NORMALIZE_RE = re.compile(r"[\s\W_]+", re.UNICODE)


def _normalize_text(content: str) -> str:
    return _NORMALIZE_RE.sub("", content.lower())


def _is_too_short(content: str) -> bool:
    return len(content.strip()) <= 2


def validate_chatbot_input(content: str) -> None:
    _validate_input_content(content)
    _validate_prompt_injection(content)
    _validate_profanity(content)


def _validate_input_content(content: str) -> None:
    if not content or not content.strip():
        raise ValidationError("메시지를 입력해주세요.")
    if len(content) > MAX_INPUT_LENGTH:
        raise ValidationError("메시지는 최대 500자까지 입력할 수 있습니다.")


def _validate_prompt_injection(content: str) -> None:
    raw_lower = content.lower()
    normalized = _normalize_text(content)
    for keyword in BLOCKED_PROMPT_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("해당 요청은 처리할 수 없습니다.")


def _validate_profanity(content: str) -> None:
    raw_lower = content.lower()
    normalized = _normalize_text(content)
    for keyword in BLOCKED_PROFANITY_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("부적절한 표현이 포함되어 있습니다.")


def is_meaningful_turn(content: str) -> bool:
    if _is_too_short(content):
        return False
    raw_lower = content.lower()
    normalized = _normalize_text(content)
    for keyword in BLOCKED_NONSENSE_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            return False
    return True


def should_force_fallback(meaningful_turns: int) -> bool:
    return meaningful_turns >= MAX_MEANINGFUL_TURNS


def should_force_end(total_turns: int) -> bool:
    return total_turns >= MAX_TOTAL_TURNS
