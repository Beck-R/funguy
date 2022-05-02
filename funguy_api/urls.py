from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'brew/', brew, name='brew'),  # test endpoint

    path(r'token/', TokenObtainPairView.as_view(), name='token'),
    path(r'token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path(r'send/', send, name='send'),  # send command to node(s)
    path(r'receive/', receive, name='receive'),  # receive command
    path(r'signal/', signal, name='signal'),  # command completion signal
]
