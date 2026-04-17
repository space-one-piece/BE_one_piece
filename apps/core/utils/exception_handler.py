from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler

ERROR_MESSAGES = {
    400: "필수값이 누락되었습니다.",
    401: "자격 인증 데이터가 제공되지 않았습니다.",
    403: "권한이 없습니다.",
    404: "데이터가 없습니다.",
    409: "이미 중복된 회원가입 내역이 존재합니다.",
    410: "대화 횟수를 초과했습니다. 새로운 세션을 시작해주세요.",
    429: "너무 자주 접근하였습니다.",
    503: "현재 AI 사용이 많아 잠시 뒤 사용해주세요.",
}


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = exception_handler(exc, context)

    if response is None:
        return response

    status_code = response.status_code
    if isinstance(response.data, dict) and "detail" in response.data:
        message = response.data["detail"]
    elif isinstance(response.data, list) and len(response.data) > 0:
        message = response.data[0]
    else:
        message = ERROR_MESSAGES.get(status_code, "알 수 없는 에러가 발생했습니다.")

    response.data = {"error_detail": message}  # 이거 빠졌어요!
    return response
