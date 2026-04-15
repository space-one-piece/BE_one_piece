from google import genai

from apps.chatbot.prompts.support_context import SCENT_DATA


def ask_gemini(combined_keywords: str) -> str:
    client = genai.Client()
    prompt = f"""
        너는 인공지능 조향사야. 아래의 [향수 데이터베이스]를 기반으로 사용자의 [선택 키워드]에 가장 잘 어울리는 향수를 하나 추천해줘.
        [향수 데이터베이스]
        {SCENT_DATA}

        [사용자 선택 키워드]
        {combined_keywords}

        답변은 다음 형식을 지켜줘:
        1. 추천 향수 이름 (id 포함)
        2. 추천 이유 (데이터의 profile 수치나 tags를 인용)
        3. 추천 하는 향은 하나로 제한
        4. 출력은 id 값과 추천 이유만 출력해줘
        5. 출력 형식은 json 방식으로 하며 이유는 reason 으로 해줘
        """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text
