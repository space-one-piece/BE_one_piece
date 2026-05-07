from apps.core.utils.s3_handler import image_url_edit
from config.settings.base import CF_DOMAIN


def image_url_cloud(image_url: str | None) -> str | None:
    if not image_url:
        return None

    image_data = image_url_edit(image_url)
    return f"{CF_DOMAIN}/{image_data}"
