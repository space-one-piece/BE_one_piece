from config.settings.base import *  # noqa: F403

DEBUG = False

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = ["127.0.0.1", "3.35.53.10", "fragmnt.pics"]

