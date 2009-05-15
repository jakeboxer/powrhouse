from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<object_id>[0-9]+)/done/$', 'chores.views.assign_done', 
        name="assign_done"),
    url(r'^(?P<object_id>[0-9]+)/done/(?P<hmate_id>[0-9]+)/(?P<key>[\w]+)',
        'chores.views.assign_done_no_login', name='assign_done_no_login'),
)
