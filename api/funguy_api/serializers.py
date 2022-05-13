from django.contrib.auth.models import User, Group

from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']
        extra_kwargs = {'id': {'read_only': True}}


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'permissions']


class CaptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capture
        fields = ['id', 'type', 'capture', 'timestamp']
        extra_kwargs = {'id': {'read_only': True}}


class KeylogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keylog
        fields = ['id', 'log', 'timestamp', 'log_file']
        extra_kwargs = {'id': {'read_only': True}}


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = ['id', 'command_type', 'group', 'command',
                  'repeat_at', 'issued_at', 'completed_at', ]
        extra_kwargs = {'id': {'read_only': True}}


class DiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disk
        fields = ['id', 'name', 'disk_type', 'fs_type', 'mount_point',
                  'is_removable', 'total_disk', 'disk_usage', 'disk_write', 'disk_read']
        extra_kwargs = {'id': {'read_only': True}}


class NodeSerializer(serializers.ModelSerializer):
    disks = DiskSerializer(many=True, allow_null=True)

    class Meta:
        model = Node
        fields = ['id', 'uuid', 'hash_sum', 'host_name', 'ipv4', 'first_seen', 'last_seen', 'os', 'os_release', 'os_version', 'processor', 'processor_count',
                  'min_freq', 'max_freq', 'memory_total', 'processor_freq', 'processor_temp', 'processor_usage', 'memory_usage', 'disks']
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        disks = validated_data.pop('disks')
        node = Node.objects.create(**validated_data)
        if disks is not None:
            for disk in disks:
                Disk.objects.create(node=node, **disk)

        return node

    # I think this kinda sucks but I didn't write this
    def update(self, instance, validated_data, partial=True):
        disks = validated_data.pop('disks')
        instance.host_name = validated_data.get(
            'host_name', instance.host_name)
        instance.ipv4 = validated_data.get('ipv4', instance.ipv4)
        instance.os = validated_data.get('os', instance.os)
        instance.os_release = validated_data.get(
            'os_release', instance.os_release)
        instance.os_version = validated_data.get(
            'os_version', instance.os_version)
        instance.processor = validated_data.get(
            'processor', instance.processor)
        instance.processor_count = validated_data.get(
            'processor_count', instance.processor_count)
        instance.min_freq = validated_data.get('min_freq', instance.min_freq)
        instance.max_freq = validated_data.get('max_freq', instance.max_freq)
        instance.memory_total = validated_data.get(
            'memory_total', instance.memory_total)
        instance.processor_freq = validated_data.get(
            'processor_freq', instance.processor_freq)
        instance.processor_temp = validated_data.get(
            'processor_temp', instance.processor_temp)
        instance.processor_usage = validated_data.get(
            'processor_usage', instance.processor_usage)
        instance.memory_usage = validated_data.get(
            'memory_usage', instance.memory_usage)
        instance.save()

        if disks is not None:
            for disk in disks:
                if 'id' in disk:
                    # update
                    instance_disk = Disk.objects.get(id=disk['id'])
                    instance_disk.name = disk.get(
                        'name', instance_disk.name)
                    instance_disk.disk_type = disk.get(
                        'disk_type', instance_disk.disk_type)
                    instance_disk.fs_type = disk.get(
                        'fs_type', instance_disk.fs_type)
                    instance_disk.mount_point = disk.get(
                        'mount_point', instance_disk.mount_point)
                    instance_disk.is_removable = disk.get(
                        'is_removable', instance_disk.is_removable)
                    instance_disk.total_disk = disk.get(
                        'total_disk', instance_disk.total_disk)
                    instance_disk.disk_usage = disk.get(
                        'disk_usage', instance_disk.disk_usage)
                    instance_disk.disk_write = disk.get(
                        'disk_write', instance_disk.disk_write)
                    instance_disk.disk_read = disk.get(
                        'disk_read', instance_disk.disk_read)
                    instance_disk.save()

        return(instance)
