from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class ShareChannel(str, Enum):
    kakao = "kakao"
    discord = "discord"


class ShareRequest(BaseModel):
    channels: List[ShareChannel]  # 어느 채널로 보낼지
    text: Optional[str] = None  # 텍스트 메시지
    url: Optional[HttpUrl] = None  # 공유할 URL
    image_url: Optional[HttpUrl] = None  # 이미지 URL (원격)
    # 파일 업로드는 multipart/form-data로 별도 엔드포인트에서 처리


class ChannelResult(BaseModel):
    channel: ShareChannel
    success: bool
    message: str


class ShareResponse(BaseModel):
    results: List[ChannelResult]
