from django.db.models import QuerySet

from apps.question.models import Keyword


def keyword_select() -> QuerySet[Keyword]:
    keyword_data = Keyword.objects.all()
    return keyword_data


def keyword_result(user, validated_data: list):
    if validated_data is None:
        return None

    # keyword_strings = [f"{data['keyword_division']: {data['keyword_name']}}" for data in validated_data]

    # json_str = json.dumps(keyword_strings, ensure_ascii=False)
