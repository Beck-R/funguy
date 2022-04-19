from tokenize import group
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from ..models import Command, Node
from ..serializers import CommandSerializer
from .utils import get_ip


@api_view(('POST',))
def send(request):
    # checking if this command is addressed to a specific node, or all nodes
    # specific node
    try:
        hash_sum = request.data["hash_sum"]
        node = get_object_or_404(Node, hash_sum=hash_sum)
        serializer = CommandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(node=node)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # all nodes
    except KeyError:
        Nodes = Node.objects.all()
        for node in Nodes:
            serializer = CommandSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(node=node)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(('GET',))
def receive(request):
    hash_sum = request.headers["hash-sum"]

    # update last contact of node
    node = get_object_or_404(Node, hash_sum=hash_sum)
    node.last_seen = timezone.now()
    node.ipv4 = get_ip(request)
    node.save()

    # find commands that aren't completed, for this node, and all nodes
    commands = Command.objects.filter(
        Q(recieved_at__isnull=True, node=node))
    serializer = CommandSerializer(commands, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('GET',))
def signal(request):
    hash_sum = request.headers["hash-sum"]
    command_id = request.headers["command-id"]

    # update last contact of node
    node = get_object_or_404(Node, hash_sum=hash_sum)
    node.last_seen = timezone.now()
    node.ipv4 = get_ip(request)
    node.save()

    command = get_object_or_404(Command, id=command_id)
    if command.node != node:
        # may want to blacklist node, because it would only signal a command it doesn't
        # own if tampering is involved.
        return Response(status=status.HTTP_400_BAD_REQUEST)

    command.received_at = timezone.now()
    command.save()
    return Response(status=status.HTTP_200_OK)
