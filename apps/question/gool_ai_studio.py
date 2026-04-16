import os

from google import genai
from google.genai.errors import ServerError
from rest_framework.exceptions import APIException


class CustomBadRequest(APIException):
    status_code = 429
    default_detail = "현재 AI 사용이 많아 잠시뒤 사용해주세요"
    default_code = "Too Mony Requests"


def ask_gemini(prompt: str) -> str | None:
    client = genai.Client(api_key=os.getenv("PJG_GEMINI_KEY"))

    try:
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt)
        return response.text
    except ServerError:
        raise CustomBadRequest()
