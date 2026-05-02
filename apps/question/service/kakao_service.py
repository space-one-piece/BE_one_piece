import json

import requests
from django.conf import settings

from apps.question.service.image_user_service import ImageUserService

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_MESSAGE_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


def get_access_token(code: str) -> str:
    """인가코드 → access_token 교환"""
    resp = requests.post(
        KAKAO_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URIS,
            "code": code,
        },
        timeout=10,
    )
    data = resp.json()
    if "access_token" not in data:
        raise ValueError(data.get("error_description", "토큰 발급 실패"))
    return data["access_token"]


def send_kakao(data: dict, access_token: str) -> dict:
    image_url = ImageUserService.web_share(data["result_id"], data["type"])
    template = {
        "object_type": "feed",
        "content": {
            "title": data.get("text", "공유된 이미지"),
            "image_url": image_url,
            "link": {
                "web_url": data.get("url", image_url),
                "mobile_web_url": data.get("url", image_url),
            },
        },
    }
    resp = requests.post(
        KAKAO_MESSAGE_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"template_object": json.dumps(template, ensure_ascii=False)},
        timeout=10,
    )

    if resp.status_code == 200:
        return {"channel": "kakao", "success": True, "message": "카카오톡 전송 성공"}
    return {"channel": "kakao", "success": False, "message": resp.text}
