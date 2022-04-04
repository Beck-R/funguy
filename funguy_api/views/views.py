from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response


from funguy_api.views.utils import get_ip
from ..serializers import *
from ..models import *


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


# can probably go back and just overwrite certain ModelViewSet methods
class NodeViewSet(viewsets.ViewSet):
    serializer_class = NodeSerializer

    def list(self, request):
        queryset = Node.objects.all()
        serializer = NodeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Node.objects.all()
        node = get_object_or_404(queryset, pk=pk)
        serializer = NodeSerializer(node)
        return Response(serializer.data)

    def create(self, request):
        request.data["ipv4"] = get_ip(request)
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        node = get_object_or_404(Node, pk=pk)
        node.last_seen = timezone.now()
        serializer = NodeSerializer(node, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        node = get_object_or_404(Node, pk=pk)
        node.last_seen = timezone.now()
        serializer = NodeSerializer(node, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        node = get_object_or_404(Node, pk=pk)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
