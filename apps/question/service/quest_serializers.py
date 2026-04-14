from apps.question.models import Question


def quest_select():
    random_question = Question.objects.select_related("QuestionsAnswer").order_by("?")[:10]
    return random_question
