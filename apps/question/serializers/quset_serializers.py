from typing import Any

from rest_framework import serializers

from apps.question.models import Question, QuestionsAnswer


class QuestionsAnswerSerializer(serializers.ModelSerializer[QuestionsAnswer]):
    content = serializers.CharField(source="answer")

    class Meta:
        model = QuestionsAnswer
        fields = ["content"]


class QuestionSerializer(serializers.ModelSerializer[Question]):
    answer = QuestionsAnswerSerializer(source="answers", read_only=True, many=True)
    title = serializers.CharField(source="content")

    class Meta:
        model = Question
        fields = ["id", "title", "additional", "left_label", "right_label", "answer"]


class QuestionsInSerializer(serializers.Serializer[Any]):
    title = serializers.CharField()
    results = serializers.CharField()
    question_num = serializers.IntegerField()
