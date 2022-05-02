from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(('GET',))
def brew(request):
    return Response("I'm nothing but a teapot", status=status.HTTP_418_IM_A_TEAPOT)
