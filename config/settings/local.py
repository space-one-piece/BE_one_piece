from config.settings.base import *  # noqa: F403

DEBUG = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = ["127.0.0.1", "54.180.148.230", "fragmnt.pics"]
