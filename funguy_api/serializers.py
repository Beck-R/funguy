from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'groups']
        extra_kwargs = {'password': {'write_only': True},
                        'id': {'read_only': True}}


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'permissions']


class PartitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partition
        fields = ['id', 'partition_name', 'partition_fstype', 'partition_mount',
                  'total_partition', 'partition_usage', 'partition_write', 'partition_read']
        extra_kwargs = {'id': {'read_only': True}}


class DiskSerializer(serializers.ModelSerializer):
    partitions = PartitionSerializer(many=True, allow_null=True)

    class Meta:
        model = Disk
        fields = ['id', 'disk_name', 'total_disk',
                  'disk_usage', 'disk_write', 'disk_read', 'partitions']
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        partitions = validated_data.pop('partitions')
        disk = Disk.objects.create(**validated_data)
        for partition in partitions:
            Partition.objects.create(disk=disk, **partition)
        return disk

    def update(self, instance, validated_data):
        pass


class NodeSerializer(serializers.ModelSerializer):
    disks = DiskSerializer(many=True, allow_null=True)

    class Meta:
        model = Node
        fields = ['id', 'host_name', 'ipv4', 'port', 'first_seen', 'last_seen', 'os',
                  'os_release', 'os_version', 'device', 'processor', 'min_freq', 'max_freq', 'disks']
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        disks = validated_data.pop('disks')
        node = Node.objects.create(**validated_data)
        if disks is not None:
            for disk in disks:
                partitions = disk.pop('partitions')
                new_disk = Disk.objects.create(node=node, **disk)

            if partitions is not None:
                for partition in partitions:
                    Partition.objects.create(disk=new_disk, **partition)

        return node

    def update(self, instance, validated_data):
        pass
