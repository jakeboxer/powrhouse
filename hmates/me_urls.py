from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_change

urlpatterns = patterns('',
    url(r'^edit/$', 'hmates.views.me_edit', name='me_edit'),
    url(r'^password/edit/$', password_change, 
        {"post_change_redirect": '/me/password/edit/done/'}, name="pw_edit"),
    url(r'^password/edit/done/$', 'hmates.views.pw_edit_done',
        name="pw_edit_done"),
    url(r'^day/$', login_required(direct_to_template),
        {"template": "me/my_day.html"}, name="my_day"),
    url(r'^$', login_required(direct_to_template),
        {"template": "me/detail.html"}, name='me'),
)
