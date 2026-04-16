from typing import Any

from rest_framework import serializers

from apps.question.models import Question, QuestionsAnswer


class QuestionsAnswerSerializer(serializers.ModelSerializer[QuestionsAnswer]):
    content = serializers.CharField(source="answer")

    class Meta:
        model = QuestionsAnswer
        fields = ["content", "score"]


class QuestionSerializer(serializers.ModelSerializer[Question]):
    answer = QuestionsAnswerSerializer(source="answers", read_only=True, many=True)
    title = serializers.CharField(source="content")

    class Meta:
        model = Question
        fields = ["title", "additional", "answer"]


class QuestionsInSerializer(serializers.Serializer[Any]):
    title = serializers.CharField()
    results = serializers.CharField()
    score = serializers.IntegerField()
    question_num = serializers.CharField()
