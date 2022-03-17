from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'permissions']


class PartitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partition
        fields = ['id', 'partition_name', 'partition_fstype', 'partition_mount',
                  'total_partition', 'partition_usage', 'partition_write', 'partition_read']


class DiskSerializer(serializers.ModelSerializer):
    partitions = PartitionSerializer(many=True, allow_null=True)

    class Meta:
        model = Disk
        fields = ['id', 'disk_name', 'total_disk',
                  'disk_usage', 'disk_write', 'disk_read']

    def create(self, validated_data):
        partitions_data = validated_data.pop('partitions')
        disk = Disk.objects.create(**validated_data)
        for partition_data in partitions_data:
            Disk.objects.create(disk=disk, **partition_data)
        return disk


class NodeSerializer(serializers.ModelSerializer):
    disks = DiskSerializer(many=True, allow_null=True)

    class Meta:
        model = Node
        fields = ['id', 'host_name', 'ipv4', 'port', 'first_seen', 'last_seen', 'os',
                  'os_release', 'os_version', 'device', 'processor', 'min_freq', 'max_freq']

    def create(self, validated_data):
        disks = validated_data.pop('disks')
        node = Node.objects.create(**validated_data)
        for disk in disks:
            Node.objects.create(node=node, **disks)
        return node
