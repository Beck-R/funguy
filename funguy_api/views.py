from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


from .serializers import *
from .models import *


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class NodeViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Node.objects.all()
        serializer = NodeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Node.objects.all()
        node = get_object_or_404(queryset, pk=pk)
        serializer = NodeSerializer(node, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiskViewSet(viewsets.ModelViewSet):
    serializer_class = DiskSerializer
    queryset = Disk.objects.all()


class PartitionViewSet(viewsets.ModelViewSet):
    serializer_class = PartitionSerializer
    queryset = Partition.objects.all()
