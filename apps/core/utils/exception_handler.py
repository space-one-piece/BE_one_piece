from typing import Any

from django.http import Http404
from rest_framework.exceptions import NotFound
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
    if isinstance(exc, Http404):
        exc = NotFound()

    response = exception_handler(exc, context)

    if response is None:
        return response

    status_code = response.status_code
    error_code = getattr(exc, "default_code", "ERROR").upper()
    original_data = response.data

    message = ""

    if hasattr(exc, "detail"):
        if isinstance(exc.detail, dict) and exc.detail:
            first_key = next(iter(exc.detail))
            first_error = exc.detail[first_key]

            if isinstance(first_error, list) and len(first_error) > 0:
                error_code = getattr(first_error[0], "code", error_code).upper()

            message = ", ".join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in exc.detail.items()])

        elif isinstance(exc.detail, list) and len(exc.detail) > 0:
            error_code = getattr(exc.detail[0], "code", error_code).upper()
            message = str(exc.detail[0])

    if not message:
        if isinstance(original_data, dict):
            message = original_data.get("detail", ERROR_MESSAGES.get(status_code, "에러가 발생했습니다."))
        elif isinstance(original_data, list) and len(original_data) > 0:
            message = original_data[0]
        else:
            message = ERROR_MESSAGES.get(status_code, "알 수 없는 에러가 발생했습니다.")

    response.data = {"status": status_code, "code": error_code, "message": str(message), "error_detail": original_data}

    return response
