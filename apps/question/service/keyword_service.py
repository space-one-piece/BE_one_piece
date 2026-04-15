from django.db.models import QuerySet

from apps.question.models import Keyword


def keyword_select() -> QuerySet[Keyword]:
    keyword_data = Keyword.objects.all()
    return keyword_data
