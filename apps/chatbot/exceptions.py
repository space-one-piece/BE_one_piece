from rest_framework.exceptions import APIException


class GeminiUnavailableError(APIException):
    status_code = 503
    default_detail = "현재 AI 사용이 많아 잠시 뒤 사용해주세요."
    default_code = "service_unavailable"


class SessionExpiredError(APIException):
    status_code = 410
    default_detail = "대화 횟수를 초과했습니다. 새로운 세션을 시작해주세요."
    default_code = "session_expired"
