from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^close/(?P<slug>[-a-zA-Z0-9]+)/(?P<hmate_pk>[0-9]+)/$',
        'top_notices.views.close', name="top_notice_close"),
)