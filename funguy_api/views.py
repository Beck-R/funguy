from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


from .serializers import *
from .models import *


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class NodeViewSet(viewsets.ModelViewSet):
    serializer_class = NodeSerializer
    queryset = Node.objects.all()

    def perform_destroy(self, instance):
        node = instance.node
        instance.delete()
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DiskViewSet(viewsets.ModelViewSet):
    serializer_class = DiskSerializer
    queryset = Disk.objects.all()


class PartitionViewSet(viewsets.ModelViewSet):
    serializer_class = PartitionSerializer
    queryset = Partition.objects.all()


class BrewViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response("I'm nothing but a teapot", status=status.HTTP_418_IM_A_TEAPOT)
