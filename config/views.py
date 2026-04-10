from django.http import HttpRequest, HttpResponse


def hellow_word(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>Hello World</h1>")
