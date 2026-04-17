import json
import time
from typing import Any

from django.conf import settings
from google import genai
from google.genai import types
from rest_framework.exceptions import APIException

from ..prompts.chatbot_prompts import CHATBOT_SYSTEM_PROMPT
from ..prompts.support_context import SCENT_DATA
from .context_service import Context, init_context, rule_based_extract

client = genai.Client(api_key=settings.LGB_GEMINI_KEY)


class GeminiUnavailableError(APIException):
    status_code = 503
    default_detail = "현재 AI 사용이 많아 잠시 뒤 사용해주세요."
    default_code = "service_unavailable"


class SessionExpiredError(APIException):
    status_code = 410
    default_detail = "대화 횟수를 초과했습니다. 새로운 세션을 시작해주세요."
    default_code = "session_expired"


PARSE_PROMPT = """
사용자의 메시지에서 다음 4가지 정보를 추출해줘.

- space: 공간 (bedroom, livingroom, bathroom, study, kitchen, office, entryway)
- mood: 분위기 (calm, fresh, romantic, focus, energetic, luxury, cozy, sweet)
- intensity: 강도 (light, medium, strong)
- time: 시간대 (morning, daytime, evening, night)

반드시 아래 JSON 형식으로만 반환해줘. 다른 말 하지 마.
없으면 null로 반환해줘.

{
  "space": "bedroom" | null,
  "mood": "calm" | null,
  "intensity": "light" | null,
  "time": "night" | null
}
"""


def llm_parse(text: str) -> Context:
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=f"{PARSE_PROMPT}\n\n사용자 입력: {text}",
        )
        raw = response.text
        if raw is None:
            return init_context()
        parsed = json.loads(raw.strip())
        return {
            "space": parsed.get("space"),
            "mood": parsed.get("mood"),
            "intensity": parsed.get("intensity"),
            "time": parsed.get("time"),
        }
    except Exception as e:
        print(f"[llm_parse error] {e}")
        return init_context()


def parse_context(text: str) -> Context:
    llm_result = llm_parse(text)
    rule_result = rule_based_extract(text)
    return {
        "space": llm_result["space"] or rule_result["space"],
        "mood": llm_result["mood"] or rule_result["mood"],
        "intensity": llm_result["intensity"] or rule_result["intensity"],
        "time": llm_result["time"] or rule_result["time"],
    }


def build_scent_context(candidates: list[dict[str, Any]]) -> str:
    lines = []
    for scent in candidates:
        lines.append(
            f"ID: {scent['id']} | 이름: {scent['name']} | "
            f"카테고리: {scent['category']} | 태그: {', '.join(scent['tags'])}"
        )
    return "\n".join(lines)


def _call_gemini(
    contents: list[types.Content],
    system_prompt: str,
    model: str,
) -> str:
    response = client.models.generate_content(
        model=model,
        contents=contents,  # type: ignore[arg-type]
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    return response.text or ""


def get_ai_response(
    messages: list[dict[str, Any]],
    candidates: list[dict[str, Any]] | None = None,
) -> str:
    system_prompt = CHATBOT_SYSTEM_PROMPT

    if candidates:
        scent_context = build_scent_context(candidates)
        system_prompt += f"\n\n## 추천 가능한 향수 후보\n{scent_context}"

    contents = [
        types.Content(
            role=msg["role"],
            parts=[types.Part(text=msg["parts"][0]["text"])],
        )
        for msg in messages
    ]

    for i in range(3):
        try:
            return _call_gemini(contents, system_prompt, settings.GEMINI_MODEL)
        except Exception as e:
            print(f"[Gemini error - retry {i}] {e}")
            if "503" in str(e):
                time.sleep(1.5 * (i + 1))
                continue
            break

    try:
        print("[Gemini fallback] switching to gemini-2.0-flash")
        return _call_gemini(contents, system_prompt, "gemini-2.0-flash")
    except Exception as e:
        print(f"[Gemini fallback error] {e}")

    raise GeminiUnavailableError()


def extract_recommended_scent_id(response_text: str) -> int | None:
    try:
        for scent in SCENT_DATA:
            if scent["name"] in response_text or scent["englishName"] in response_text:
                return int(scent["id"])
    except Exception as e:
        print(f"[extract error] {e}")
        return None
    return None
