from django.http import HttpResponse

from rest_framework import status


def brew(request):
    return HttpResponse("I'm nothing but a teapot", status=status.HTTP_418_IM_A_TEAPOT)
