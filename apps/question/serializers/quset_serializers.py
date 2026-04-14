from rest_framework import serializers

from apps.question.models import Question, QuestionsAnswer


class QuestionsAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionsAnswer
        fields = ["answer", "score"]


class QuestionSerializer(serializers.ModelSerializer):
    answer = QuestionsAnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ["content", "answer"]
