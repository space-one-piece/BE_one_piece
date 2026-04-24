import base64
import time

from google import genai
from google.genai.errors import ServerError
from rest_framework.exceptions import APIException

from config.settings.base import GEMINI_MODEL, PJG_GEMINI_KEY


class CustomBadRequest(APIException):
    status_code = 429
    default_detail = "현재 AI 사용이 많아 잠시뒤 사용해주세요"
    default_code = "Too Many Requests"


class Gemini:
    _client = genai.Client(api_key=PJG_GEMINI_KEY)

    @classmethod
    def ask_gemini(cls, prompt: str, max_retries: int = 3) -> str | None:
        if max_retries == 0:
            raise CustomBadRequest()

        try:
            response = cls._client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return response.text
        except ServerError:
            time.sleep(5)
            max_retries = max_retries - 1
            return cls.ask_gemini(prompt, max_retries)

    @classmethod
    def image_gemini(cls, prompt: str) -> str | None:
        try:
            response = cls._client.models.generate_content(model="gemini-2.5-flash-image", contents=prompt)

            if response is not None and response.parts is not None:
                for part in response.parts:
                    if part.inline_data is not None:
                        image = part.as_image()
                        if image is not None:
                            image_byte = image.image_bytes
                            if image_byte is not None:
                                base64_data = base64.b64encode(image_byte).decode("utf-8")
                                return f"data:image/jpg;base64,{base64_data}"

            return None
        except ServerError:
            raise CustomBadRequest()
