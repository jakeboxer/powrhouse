from django.contrib import admin
from top_notices.models import *

class TopNoticeSlugAdmin (admin.ModelAdmin): pass
admin.site.register(TopNoticeSlug, TopNoticeSlugAdmin)

class TopNoticeClosingAdmin (admin.ModelAdmin): pass
admin.site.register(TopNoticeClosing, TopNoticeClosingAdmin)