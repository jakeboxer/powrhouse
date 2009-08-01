from django.db import models
from hmates.models import Housemate
import datetime

class TopNoticeSlug (models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    
    def __unicode__ (self):
        return self.slug

class TopNoticeClosing (models.Model):
    top_notice = models.ForeignKey(TopNoticeSlug)
    hmate      = models.ForeignKey(Housemate)
    closed_at  = models.DateTimeField(blank=False, null=False,
        default=datetime.datetime.utcnow)
    
    def __unicode__ (self):
        return "%s closed '%s'" \
            % (self.hmate.get_full_name(), self.top_notice.slug)