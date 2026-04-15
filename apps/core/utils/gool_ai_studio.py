import os

import google.generativeai as genai


class ChatBot:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=os.environ.get("GEN_AI_CLIENT_KEY"))
        self.model = genai.GenerativeModel(model_name)

    def ask_gemini(self, combined_keywords: str):
        prompt = f"""
        사용자가 선택한 키워드들입니다: {combined_keywords}
        이 키워드들을 바탕으로 어울리는 향수를 추천해줘.
        """

        response = self.model.generate_content(prompt)

        return response.text

    def image_base64(self, perfume_mood: str) -> str:
        pass
