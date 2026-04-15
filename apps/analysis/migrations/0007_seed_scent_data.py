import json
import os

from django.db import migrations


def load_scent_data(apps, schema_editor):
    Scent = apps.get_model("analysis", "Scent")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "../scent-mock-data-30.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

        for item in data:
            Scent.objects.get_or_create(
                eng_name=item["englishName"],
                defaults={
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "categories": item.get("category", ""),
                    "tags": item.get("tags", []),
                    "keywords": item.get("keywords", []),
                    "similar_scents": item.get("similarScents", []),
                    "is_bestseller": item.get("isBestseller", False),
                    "intensity": item.get("intensity", 0),
                    "scent_notes": item.get("notes", {}),
                    "profile": item.get("profile", {}),
                    "season": item.get("season", []),
                    "recommended_places": item.get("recommendedPlaces", []),
                    "thumbnail_url": "",
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("analysis", "0006_scent_keywords_scent_tags_scent_scent_tags_gin_and_more"),
    ]

    operations = [
        migrations.RunPython(load_scent_data),
    ]
