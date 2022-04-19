from django.db import models
from django.utils import timezone
import datetime


# Node related models
class Node(models.Model):
    # Connection Info
    hash_sum = models.CharField(max_length=512, unique=True)
    host_name = models.CharField(max_length=512)
    ipv4 = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True)
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
        return f'{self.host_name}:{self.hash_sum}'

    # if node has contacted server in last two hours, set as active
    def is_active(self):
        now = timezone.now()
        return self.last_seen >= now - datetime.timedelta(hours=2)


class Disk(models.Model):
    disk_name = models.CharField(max_length=512)
    total_disk = models.IntegerField()
    disk_usage = models.IntegerField()
    disk_write = models.IntegerField()
    disk_read = models.IntegerField()

    node = models.ForeignKey(Node, related_name='disks',
                             on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.node.host_name}:{self.disk_name}'


class Partition(models.Model):
    partition_name = models.CharField(max_length=512)
    partition_fstype = models.CharField(max_length=512)
    partition_mount = models.CharField(max_length=512)
    total_partition = models.IntegerField()
    partition_usage = models.IntegerField()
    partition_write = models.IntegerField()
    partition_read = models.IntegerField()

    disk = models.ForeignKey(Disk, related_name='partitions',
                             on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.disk.disk_name}:{self.partition_name}'


class Command(models.Model):
    shell_type = (
        ('default', 'Default'),
        ('bash', 'Bash'),
        ('zsh', 'Zsh'),
        ('powershell', 'Powershell'),
    )
    command_type = (
        ('shell', 'Shell'),
        ('macro', 'Macro'),
        ('script', 'Script'),
        ('scheduled', 'Scheduled'),
    )
    group_type = (
        ('all', 'All'),
        ('individual', 'Individual'),
    )

    hash_sum = models.CharField(max_length=512, null=True, blank=True)
    node = models.ForeignKey(
        Node, related_name='commands', on_delete=models.CASCADE, null=True, blank=True)
    group = models.CharField(
        max_length=32, choices=group_type, default='all')

    shell = models.CharField(
        max_length=32, choices=shell_type, default='default')
    type = models.CharField(
        max_length=32, choices=command_type, default='shell')
    command = models.TextField(null=True, blank=True)
    script = models.FileField(upload_to='scripts/', null=True, blank=True)

    repeat_at = models.DateTimeField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        # infer if it is a group or individual command
        if self.node:
            return f'{self.node.host_name}:{self.command}'
        else:
            return f'{self.group}:{self.command}'
