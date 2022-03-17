from django.urls import path, include

from funguy_api.views import *
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers


# nested routing
# router = nested_routers.SimpleRouter()
# router.register(r'nodes', NodeViewSet)

# disk_router = routers.NestedSimpleRouter(
#     router, r'nodes', lookup='node')
# disk_router.register(r'disks', DiskViewSet, basename='node-disks')

# partition_router = routers.NestedSimpleRouter(
#     disk_router, r'disks', lookup='disk')
# partition_router.register(
#     r'partitions', PartitionViewSet, basename='node-disks-partitions')


# standard routing
router = DefaultRouter()
router.register(r'nodes', NodeViewSet)
router.register(r'disks', DiskViewSet)
router.register(r'partitions', PartitionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('', include(disk_router.urls)),
]
