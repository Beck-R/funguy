from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from funguy_api.views.views import *
from funguy_api.views.brew import brew
from funguy_api.views.command import send, receive, signal


# standard routing
router = DefaultRouter()

router.register(r'node', NodeViewSet, basename='node')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'brew/', brew, name='brew'),  # test endpoint
    path(r'send/', send, name='send'),  # send command to node(s)
    path(r'receive/', receive, name='receive'),  # receive command
    path(r'signal/', signal, name='signal'),  # command completion
]
