from django.contrib import admin
from chores.models import *

class ChoreAdmin (admin.ModelAdmin): pass
admin.site.register(Chore, ChoreAdmin)

class AssignmentAdmin (admin.ModelAdmin): pass
admin.site.register(Assignment, AssignmentAdmin)