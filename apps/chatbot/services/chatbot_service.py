import json
import re
import time
from typing import Any

from django.conf import settings
from google import genai
from google.genai import types

from ..exceptions import GeminiUnavailableError
from ..prompts.chatbot_prompts import CHATBOT_SYSTEM_PROMPT
from .context_service import Context, init_context, rule_based_extract

client = genai.Client(api_key=settings.LGB_GEMINI_KEY)

PARSE_PROMPT = """
사용자의 메시지에서 다음 4가지 정보를 추출해줘.

- space: 사용자가 향기를 사용할 공간
  (bedroom, livingroom, bathroom, study, kitchen, office, entryway)
  예) "밖에서", "외출용", "외부" → entryway 또는 office
      "야외", "나들이", "데이트" → entryway
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
        "space": llm_result["space"] if llm_result["space"] is not None else rule_result["space"],
        "mood": llm_result["mood"] if llm_result["mood"] is not None else rule_result["mood"],
        "intensity": llm_result["intensity"] if llm_result["intensity"] is not None else rule_result["intensity"],
        "time": llm_result["time"] if llm_result["time"] is not None else rule_result["time"],
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
    excluded_ids: list[int] | None = None,
) -> dict[str, Any]:
    system_prompt = CHATBOT_SYSTEM_PROMPT

    if candidates:
        scent_context = build_scent_context(candidates)
        system_prompt += f"\n\n## 추천 가능한 향수 후보\n{scent_context}"

    if excluded_ids:
        system_prompt += "\n\n## 이미 추천한 향수 ID (절대 다시 추천 금지)\n"
        system_prompt += f"다음 ID의 향수는 절대로 추천하지 마세요: {excluded_ids}\n"
        system_prompt += "위 ID가 scent_id로 나오면 안 됩니다. 반드시 다른 향수를 추천하세요."

    contents = [
        types.Content(
            role=msg["role"],
            parts=[types.Part(text=msg["parts"][0]["text"])],
        )
        for msg in messages
    ]

    raw_reply = ""

    for i in range(3):
        try:
            raw_reply = _call_gemini(contents, system_prompt, settings.GEMINI_MODEL)
            break
        except Exception as e:
            print(f"[Gemini error - retry {i}] {e}")
            if "503" in str(e):
                time.sleep(1.5 * (i + 1))
                continue
            break

    if not raw_reply:
        try:
            print("[Gemini fallback] switching to gemini-2.0-flash-lite")
            raw_reply = _call_gemini(contents, system_prompt, "gemini-2.0-flash-lite")
        except Exception as e:
            print(f"[Gemini fallback error] {e}")
            raise GeminiUnavailableError()

    try:
        cleaned = re.sub(r"```json|```", "", raw_reply).strip()
        parsed = json.loads(cleaned)
        scent_id = parsed.get("scent_id")

        if scent_id and excluded_ids and scent_id in excluded_ids:
            print(f"[warn] AI가 excluded_id {scent_id} 추천 시도 → 무시")
            scent_id = None

        return {
            "scent_id": scent_id,
            "reply": parsed.get("reply", ""),
        }
    except Exception as e:
        print(f"[JSON parse error] {e}, raw: {raw_reply}")
        return {
            "scent_id": None,
            "reply": raw_reply,
        }
