from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_change

urlpatterns = patterns('',
    url(r'^edit/$', 'hmates.views.me_edit', name='me_edit'),
    url(r'^password/edit/$', password_change, name='pw_edit'),
    url(r'^day/$', login_required(direct_to_template),
        {"template": "me/my_day.html"}, name="my_day"),
    url(r'^$', login_required(direct_to_template),
        {"template": "me/detail.html"}, name='me'),
)
