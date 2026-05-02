import requests
from django.conf import settings

from apps.question.service.image_user_service import ImageUserService


def send_discord(data: dict) -> dict:
    """Discord Webhook으로 메시지/이미지 전송"""
    webhook_url = settings.DISCORD_WEBHOOK_URL
    if not webhook_url:
        return {"channel": "discord", "success": False, "message": "DISCORD_WEBHOOK_URL 미설정"}

    embeds = []
    if data.get("url") or data.get("image_url"):
        embed = {"description": data.get("text", "")}
        if data.get("url"):
            embed["url"] = data["url"]
        if data.get("image_url"):
            embed["image"] = {"url": ImageUserService.web_share(data["result_id"], data["type"])}
        embeds.append(embed)

    payload = {}
    if embeds:
        payload["embeds"] = embeds
    else:
        payload["content"] = data.get("text", "")

    resp = requests.post(webhook_url, json=payload, timeout=10)

    if resp.status_code in (200, 204):
        return {"channel": "discord", "success": True, "message": "디스코드 전송 성공"}
    return {"channel": "discord", "success": False, "message": resp.text}


def send_discord_file(file, filename: str, content_type: str) -> dict:
    """파일을 Discord에 직접 첨부 전송"""
    webhook_url = settings.DISCORD_WEBHOOK_URL
    if not webhook_url:
        return {"channel": "discord", "success": False, "message": "DISCORD_WEBHOOK_URL 미설정"}

    resp = requests.post(
        webhook_url,
        files={"file": (filename, file.read(), content_type)},
        timeout=30,
    )

    if resp.status_code in (200, 204):
        return {"channel": "discord", "success": True, "message": "파일 전송 성공"}
    return {"channel": "discord", "success": False, "message": resp.text}
