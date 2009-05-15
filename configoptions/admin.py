from django.contrib import admin
from configoptions.models import *

class ConfigOptionAdmin (admin.ModelAdmin): pass
admin.site.register(ConfigOption, ConfigOptionAdmin)