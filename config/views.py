from django.http import HttpResponse


def hellow_word(request):
    return HttpResponse("<h1>Hello World</h1>")