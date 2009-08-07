from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^topnotices/close/(?P<slug>[-a-zA-Z0-9]+)/$',
        'api.views.top_notices_close'),
)