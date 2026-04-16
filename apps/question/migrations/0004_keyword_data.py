import json
import os

from django.db import migrations


def load_all_data(apps, schema_editor):
    # 1. 모델 가져오기
    Keyword = apps.get_model("question", "Keyword")
    Question = apps.get_model("question", "Question")
    Answer = apps.get_model("question", "QuestionsAnswer")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # JSON 파일들이 있는 루트 경로 (manage.py 위치)
    root_dir = os.path.normpath(os.path.join(current_dir, "../seed_data/"))

    # --- [1] 키워드 데이터 로드 (keyword-seed-data.json) ---
    keyword_path = os.path.join(root_dir, "keyword-seed-data.json")
    if os.path.exists(keyword_path):
        with open(keyword_path, "r", encoding="utf-8") as f:
            keywords = json.load(f)
            for item in keywords:
                fields = item.get("fields", {})
                Keyword.objects.get_or_create(
                    id=item.get("pk"),
                    defaults={
                        "division": fields.get("division"),
                        "name": fields.get("name"),
                    },
                )

    # --- [2] 질문 데이터 로드 (questions-seed-data.json) ---
    question_path = os.path.join(root_dir, "question-seed-data.json")
    if os.path.exists(question_path):
        with open(question_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
            for item in questions:
                Question.objects.get_or_create(
                    id=item["id"], defaults={"content": item["content"], "additional": item.get("additional", "")}
                )

    # --- [3] 답변 데이터 로드 (answers-seed-data.json) ---
    answer_path = os.path.join(root_dir, "answers-seed-data.json")
    if os.path.exists(answer_path):
        with open(answer_path, "r", encoding="utf-8") as f:
            answers = json.load(f)
            for item in answers:
                try:
                    q_obj = Question.objects.get(id=item["question_id"])
                    Answer.objects.get_or_create(
                        question=q_obj,
                        answer=item["answer"],  # 모델 필드명이 answer인 경우
                        defaults={"score": item["score"]},
                    )
                except Question.DoesNotExist:
                    continue


class Migration(migrations.Migration):
    dependencies = [
        ("question", "0003_question_additional"),  # 이전 마이그레이션 파일 확인
    ]

    operations = [
        migrations.RunPython(load_all_data),
    ]
