from django.contrib import admin
from hholds.models import *

class HouseholdAdmin (admin.ModelAdmin): pass
admin.site.register(Household, HouseholdAdmin)