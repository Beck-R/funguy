from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models import *
from ..serializers import *


@api_view(('POST',))
def send_command(request):
    hash_sum = request.data["hash_sum"]
    node = get_object_or_404(Node, hash_sum=hash_sum)
    serializer = CommandSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(node=node)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
