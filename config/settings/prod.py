from config.settings.base import *  # noqa: F403

DEBUG = False

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = ["127.0.0.1", "52.79.249.237", "fragmnt.pics"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://fragmnt.pics/api/docs/",
    "https://fe-one-piece.vercel.app",
]
