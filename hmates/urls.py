from django.conf.urls.defaults import *
from django.template import RequestContext
from django.views.generic.list_detail import object_detail
from django.views.generic.create_update import update_object, delete_object
from django.contrib.auth.decorators import login_required, permission_required
from hmates.decorators import must_live_together, target_must_be_inactive
from hmates.models import Housemate

hmate_detail_dict = {
    "queryset": Housemate.objects.all(),
    "template_name": "hmates/detail.html",
    "template_object_name": "hmate"
}

urlpatterns = patterns('',
    url(r'^(?P<object_id>[0-9]+)/$',
        login_required(must_live_together(object_detail)), 
        hmate_detail_dict, name='hmate_detail'),
    url(r'^(?P<object_id>[0-9]+)/edit/$', "hmates.views.edit_inactive", 
        name='hmate_edit_inactive'),
    url(r'^(?P<object_id>[0-9]+)/resend/$', 'hmates.views.resend_add_email',
        name='resend_add_email'),
    url(r'^(?P<object_id>[0-9]+)/boot/$', 'hmates.views.boot',
        name='hmate_boot'),
    url(r'^number/$', 'hmates.views.num', name='num_hmates'),
    url(r'^add/(?P<num_hmates>[0-9]+)/$', 'hmates.views.add_multiple', 
        name='hmate_add_multiple'),
)
