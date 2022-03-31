from django.urls import path, include

from funguy_api.views import *
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers


# standard routing
router = DefaultRouter()

router.register(r'nodes', NodeViewSet, basename='node')
router.register(r'brew', BrewViewSet, basename='brew')

urlpatterns = [
    path('', include(router.urls)),
]
