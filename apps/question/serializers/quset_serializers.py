from rest_framework import serializers

from apps.question.models import Question, QuestionsAnswer


class QuestionsAnswerSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source="answer")
    num = serializers.CharField(source="score")

    class Meta:
        model = QuestionsAnswer
        fields = ["content", "num"]


class QuestionSerializer(serializers.ModelSerializer):
    answer = QuestionsAnswerSerializer(read_only=True)
    title = serializers.CharField(source="content")

    class Meta:
        model = Question
        fields = ["title", "answer"]
