from django.db import models
from hmates.models import Housemate
import datetime

class TopNoticeSlug (models.Model):
    slug = models.SlugField(max_length=50, unique=True)

class TopNoticeClosing (models.Model):
    top_notice = models.ForeignKey(TopNoticeSlug)
    hmate      = models.ForeignKey(Housemate)
    closed_at  = models.DateTimeField(blank=False, null=False,
        default=datetime.datetime.utcnow)