from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from hholds.decorators import hhold_required
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^my/$', login_required(hhold_required(direct_to_template)),
        {"template": "hholds/my.html"}, name='my_hhold'),
    url(r'^edit/$', 'hholds.views.edit', name='hhold_edit'),
    url(r'^create/$', 'hholds.views.create', name='hhold_create'),
    url(r'^leave/$', 'hholds.views.leave', name="hhold_leave"),
    url(r'^$', 'hholds.views.hhold_branch', name='hhold_branch'),
)
