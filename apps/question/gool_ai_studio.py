from google import genai
from google.genai.errors import ServerError
from rest_framework.exceptions import APIException

from config.settings.base import GEMINI_MODEL, PJG_GEMINI_KEY


class CustomBadRequest(APIException):
    status_code = 429
    default_detail = "현재 AI 사용이 많아 잠시뒤 사용해주세요"
    default_code = "Too Mony Requests"


def ask_gemini(prompt: str) -> str | None:
    client = genai.Client(api_key=PJG_GEMINI_KEY)

    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text
    except ServerError:
        raise CustomBadRequest()
