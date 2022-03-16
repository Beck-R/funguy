from rest_framework import viewsets, status
from rest_framework.response import Response


from .serializers import *
from .models import *


class NodeViewSet(viewsets.ModelViewSet):
    serializer_class = NodeSerializer
    queryset = Node.objects.all()


class DiskViewSet(viewsets.ModelViewSet):
    serializer_class = DiskSerializer
    queryset = Disk.objects.all()


class PartitionViewSet(viewsets.ModelViewSet):
    serializer_class = PartitionSerializer
    queryset = Partition.objects.all()
