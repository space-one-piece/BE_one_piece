from rest_framework import serializers

from apps.question.models import Question, QuestionsAnswer


class QuestionsAnswerSerializer(serializers.ModelSerializer[QuestionsAnswer]):
    content = serializers.CharField(source="answer")
    num = serializers.CharField(source="score")

    class Meta:
        model = QuestionsAnswer
        fields = ["content", "num"]


class QuestionSerializer(serializers.ModelSerializer[Question]):
    answer = QuestionsAnswerSerializer(read_only=True, many=True)
    title = serializers.CharField(source="content")

    class Meta:
        model = Question
        fields = ["title", "answer"]
