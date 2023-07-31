from django.shortcuts import redirect


def redirect_login(request):
    response = redirect('/accounts/login/')
    return response


def redirect_to_weather(request):
    response = redirect('/weather/cities/')
    return response

