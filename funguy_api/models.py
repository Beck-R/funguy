from django.db import models


class Node(models.Model):
    # Connection Info
    host_name = models.CharField(max_length=512)
    ipv4 = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True)
    port = models.IntegerField()
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    # Device Info
    os = models.CharField(max_length=512)
    os_release = models.CharField(max_length=512)
    os_version = models.CharField(max_length=512)
    device = models.CharField(max_length=512)
    processor = models.CharField(max_length=512)
    min_freq = models.FloatField()
    max_freq = models.FloatField()

    def __str__(self):
        return f'/{self.host_name}'


class Disk(models.Model):
    node = models.ForeignKey(
        Node, on_delete=models.CASCADE, null=True, blank=True)
    disk_name = models.CharField(max_length=512)
    total_disk = models.IntegerField()
    disk_usage = models.IntegerField()
    disk_write = models.IntegerField()
    disk_read = models.IntegerField()

    def __str__(self):
        return f'/{self.disk_name}'


class Partition(models.Model):
    disk = models.ForeignKey(
        Disk, on_delete=models.CASCADE, null=True, blank=True)
    partition_name = models.CharField(max_length=512)
    partition_fstype = models.CharField(max_length=512)
    partition_mount = models.CharField(max_length=512)
    total_partition = models.IntegerField()
    partition_usage = models.IntegerField()
    partition_write = models.IntegerField()
    partition_read = models.IntegerField()

    def __str__(self):
        return f'/{self.partition_name}'
