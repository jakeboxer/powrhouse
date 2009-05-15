from django.contrib import admin
from hmates.models import *

class HousemateAdmin (admin.ModelAdmin): pass
admin.site.register(Housemate, HousemateAdmin)

class InviteAdmin (admin.ModelAdmin): pass
admin.site.register(Invite, InviteAdmin)