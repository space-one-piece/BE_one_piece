from django.db.models import QuerySet

from apps.question.models import Question


def quest_select() -> QuerySet[Question]:
    random_question = Question.objects.prefetch_related("answer").order_by("?")[:10]
    return random_question
