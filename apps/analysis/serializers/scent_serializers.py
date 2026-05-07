from rest_framework import serializers

from apps.analysis.models import Scent


class ScentCreateUpdateSerializer(serializers.ModelSerializer[Scent]):
    class Meta:
        model = Scent
        fields = [
            "name",
            "eng_name",
            "description",
            "categories",
            "tags",
            "keywords",
            "intensity",
            "is_bestseller",
            "scent_notes",
            "profile",
            "season",
            "recommended_places",
            "similar_scents",
            "thumbnail_url",
        ]
