from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import get_ip


@api_view(('GET',))
def brew(request):
    ip = get_ip(request)
    return Response(f"Hello {ip}, I'm nothing but a teapot", status=status.HTTP_418_IM_A_TEAPOT)
