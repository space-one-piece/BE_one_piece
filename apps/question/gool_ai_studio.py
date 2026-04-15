from google import genai

from apps.chatbot.prompts.support_context import SCENT_DATA


def ask_gemini(combined_keywords: str) -> str:
    client = genai.Client()
    prompt = f"""
        사용자가 선택한 키워드들입니다: {combined_keywords}
        이 키워드들을 바탕으로 어울리는 향수를 추천해줘
        추천할 향수 대상은 {SCENT_DATA} 이 내용을 이용해서 
        데이터를 출력하지만 하나만 추천 해서 json 방식으로 반환해줘.
        """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text
