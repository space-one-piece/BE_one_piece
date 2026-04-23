import json
import os

from django.db import migrations


def load_all_data(apps, schema_editor):
    Keyword = apps.get_model("question", "Keyword")
    Question = apps.get_model("question", "Question")
    Answer = apps.get_model("question", "QuestionsAnswer")

    Answer.objects.all().delete()
    Question.objects.all().delete()
    Keyword.objects.all().delete()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.normpath(os.path.join(current_dir, "../seed_data/"))

    keyword_path = os.path.join(root_dir, "keyword-seed-data3.json")
    if os.path.exists(keyword_path):
        with open(keyword_path, "r", encoding="utf-8") as f:
            keywords = json.load(f)
            for item in keywords:
                fields = item.get("fields", {})
                Keyword.objects.update_or_create(
                    id=item.get("pk"),
                    defaults={
                        "division": fields.get("division"),
                        "name": fields.get("name"),
                        "score": fields.get("score"),
                    },
                )

    question_path = os.path.join(root_dir, "question-seed-data3.json")
    if os.path.exists(question_path):
        with open(question_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
            for item in questions:
                Question.objects.update_or_create(
                    id=item["id"],
                    defaults={
                        "content": item["content"],
                        "additional": item.get("additional", ""),
                        "left_label": item.get("left_label", ""),
                        "right_label": item.get("right_label", ""),
                        "category": item.get("category"),
                    },
                )

    answer_path = os.path.join(root_dir, "answers-seed-data3.json")
    if os.path.exists(answer_path):
        with open(answer_path, "r", encoding="utf-8") as f:
            answers = json.load(f)
            for item in answers:
                try:
                    q_obj = Question.objects.get(id=item["question_id"])
                    Answer.objects.get_or_create(
                        question=q_obj,
                        answer=item["answer"],
                        defaults={"score": item.get("score")},
                    )
                except Question.DoesNotExist:
                    continue


class Migration(migrations.Migration):
    dependencies = [
        ("question", "0008_keyword_score_question_categories_and_more"),
    ]

    operations = [
        migrations.RunPython(load_all_data),
    ]
