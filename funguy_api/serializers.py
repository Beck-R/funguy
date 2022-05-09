from django.contrib.auth.models import User, Group

from rest_framework import serializers

from .models import *

import base64


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

    # see below
    def update(self, instance, validated_data, partial=True):
        instance.disk_name = validated_data.get(
            'disk_name', instance.disk_name)
        instance.total_disk = validated_data.get(
            'total_disk', instance.total_disk)
        instance.disk_usage = validated_data.get(
            'disk_usage', instance.disk_usage)
        instance.disk_write = validated_data.get(
            'disk_write', instance.disk_write)
        instance.disk_read = validated_data.get(
            'disk_read', instance.disk_read)
        instance.save()

        if 'partitions' in validated_data:
            instance.partitions.all().delete()
            for partition in validated_data.get('partitions'):
                Partition.objects.create(disk=instance, **partition)
        instance.save()
        return instance


class NodeSerializer(serializers.ModelSerializer):
    disks = DiskSerializer(many=True, allow_null=True)

    class Meta:
        model = Node
        fields = ['id', 'uuid', 'host_name', 'ipv4', 'first_seen', 'last_seen', 'os', 'os_release', 'os_version', 'device', 'processor', 'processor_cores',
                  'min_freq', 'max_freq', 'memory_total', 'processor_freq', 'processor_temp', 'processor_usage', 'memory_usage', 'disks']
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
        instance.device = validated_data.get('device', instance.device)
        instance.processor = validated_data.get(
            'processor', instance.processor)
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
                    instance_disk.disk_name = disk.get(
                        'disk_name', instance_disk.disk_name)
                    instance_disk.total_disk = disk.get(
                        'total_disk', instance_disk.total_disk)
                    instance_disk.disk_usage = disk.get(
                        'disk_usage', instance_disk.disk_usage)
                    instance_disk.disk_write = disk.get(
                        'disk_write', instance_disk.disk_write)
                    instance_disk.disk_read = disk.get(
                        'disk_read', instance_disk.disk_read)
                    instance_disk.save()

                    if 'partitions' in disk:
                        # update
                        for partition in disk['partitions']:
                            if 'id' in partition:
                                instance_partition = Partition.objects.get(
                                    id=partition['id'])
                                instance_partition.partition_name = partition.get(
                                    'partition_name', instance_partition.partition_name)

        return(instance)
