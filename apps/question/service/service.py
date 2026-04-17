import json
from typing import Any, cast

from apps.chatbot.prompts.support_context import SCENT_DATA
from apps.question.models import QuestionsResults


def parse_gemini_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        cleaned = cleaned.replace("json\n", "", 1)

    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]

    cleaned = cleaned.strip()

    return cast(dict[str, Any], json.loads(cleaned))


def result_prompt(combined_keywords: str, check_type: str) -> str:
    prompt = f"""
        너는 인공지능 조향사야. 아래의 [향수 데이터베이스]를 기반으로 사용자의 [선택 {check_type}]에 가장 잘 어울리는 향수를 하나 추천해줘.
        [향수 데이터베이스]
        {SCENT_DATA}

        [사용자 선택 {check_type}]
        {combined_keywords}
        답변은 다음 형식을 지켜줘:
        1. 추천 향수 이름 (id 포함)
        2. 추천 이유 (데이터의 profile 수치나 tags를 인용)
        3. 추천 하는 향은 하나로 제한
        4. 출력은 id 값과 추천 이유는 reason 으로 해줘
        5. 이유에서 사용자님 이라는 빼고 바로 향수 설명과(향수 데이터베이스 name값 그대로) profile, tags 정보를 선택한 데이터를 통해 설명을 넣어줘
        6. profile, tags 설명을 넣을때 향수 데이터베이스 정보를 맘대로 수정 하지 말고 설명해줘
        7. 출력 데이터는 데이터베이스 id 값과 이유인 reason 데이터를 json 방식으로 출력하는데 마크다운 방식은 빼고 해줘
        """
    return prompt


def keyword_save(user_id: int, scent_id: int, answer_ai: str, json_data: str, division: str) -> QuestionsResults:
    return QuestionsResults.objects.create(
        user_id=user_id, scent_id=scent_id, division=division, questions_json=json_data, answer_ai=answer_ai
    )
