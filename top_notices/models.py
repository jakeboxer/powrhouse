from django.db import models
from hmates.models import Housemate
import datetime

class TopNoticeSlug (models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    
    def has_been_closed_by (self, hmate):
        """
        Returns whether or not the top notice has been closed by the specified
        hmate.
        
        @param: hmate The housemate who may have closed the top notice
        """
        closing = TopNoticeClosing.objects.filter(top_notice=self, hmate=hmate)
        return int(closing.count()) > 0
    
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