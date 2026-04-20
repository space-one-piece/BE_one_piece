from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models

from apps.core.models import TimeStampModel
from apps.users.models.models import User


class Scent(TimeStampModel):
    name = models.CharField(max_length=100)
    eng_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    categories = models.CharField(max_length=255)
    tags = ArrayField(models.CharField(max_length=20), default=list, blank=True)
    keywords = ArrayField(models.CharField(max_length=20), default=list, blank=True)

    intensity = models.IntegerField()
    is_bestseller = models.BooleanField(null=True, blank=True)
    scent_notes = models.JSONField(null=True, blank=True)
    profile = models.JSONField(null=True, blank=True)

    season = ArrayField(models.CharField(max_length=50), null=True, blank=True)
    recommended_places = models.JSONField(default=list, null=True, blank=True)
    similar_scents = ArrayField(
        models.IntegerField(),
        null=True,
        blank=True,
    )

    thumbnail_url = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "scent"

        indexes = [
            models.Index(fields=["is_bestseller"]),
            models.Index(fields=["season"]),
            models.Index(fields=["categories"]),
            GinIndex(fields=["tags"], name="scent_tags_gin"),
            GinIndex(fields=["keywords"], name="scent_keywords_gin"),
            GinIndex(fields=["scent_notes"], name="scent_notes_gin"),
        ]


class ImageAnalysis(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_scent = models.ForeignKey(Scent, on_delete=models.CASCADE)
    s3_image_url = models.CharField(null=True, blank=True, max_length=500)
    ai_tags = models.JSONField(null=True, blank=True)
    ai_intensity = models.IntegerField(null=True, blank=True)
    ai_keywords = models.JSONField(null=True, blank=True)
    ai_comment = models.TextField(null=True, blank=True)
    match_score = models.FloatField(null=True, blank=True)
    review = models.TextField(null=True, blank=True, max_length=300)
    rating = models.IntegerField(null=True, blank=True)
    is_helpful = models.BooleanField(default=False)
    is_fallback = models.BooleanField(default=False)

    class Meta:
        db_table = "image_analysis"

        indexes = [
            models.Index(fields=["-created_at"], name="idx_created_at"),
            models.Index(fields=["user"], name="idx_user"),
            models.Index(fields=["is_helpful"], name="idx_is_helpful"),
            models.Index(fields=["is_fallback"], name="idx_is_fallback"),
        ]


class ImageColorAnalysis(TimeStampModel):
    analysis = models.OneToOneField(ImageAnalysis, on_delete=models.CASCADE, related_name="image_metadata")
    dominant_color_hex = models.JSONField(null=True, blank=True)
    contrast_ratio = models.FloatField(null=True, blank=True)
    avg_brightness = models.FloatField(null=True, blank=True)
    avg_saturation = models.FloatField(null=True, blank=True)
    is_failed = models.BooleanField(default=False, blank=True)
    error_log = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "image_color_analysis"

        indexes = [
            models.Index(fields=["is_failed"], name="idx_is_failed"),
        ]
