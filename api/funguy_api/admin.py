from django.contrib import admin

from .models import *

admin.site.register(Node)
admin.site.register(Disk)
admin.site.register(Command)
admin.site.register(Keylog)
admin.site.register(Capture)
