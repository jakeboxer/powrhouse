from django.conf.urls.defaults import *
from django.views.generic.create_update import delete_object
from django.contrib.auth.decorators import login_required, permission_required
from hmates.decorators import must_own_invite
from hmates.models import Invite

invite_decline_dict = {
    "model":                Invite,
    "post_delete_redirect": "/household/",
    "template_object_name": "invite",
    "template_name":        "invites/confirm_delete.html"
}

urlpatterns = patterns('',
    url(r'^(?P<object_id>[0-9]+)/$', 'hmates.views.invite',
        name='invite'),
    url(r'^(?P<object_id>[0-9]+)/cancel/$',
        login_required(permission_required("hmates.delete_housemate")(\
            must_own_invite(delete_object))),
        invite_decline_dict, name='invite_cancel'),
    url(r'^(?P<object_id>[0-9]+)/accept/$', 'hmates.views.invite_accept',
        name='invite_accept'),
    url(r'^(?P<object_id>[0-9]+)/decline/$', 
        'hmates.views.invite_decline', name='invite_decline'),
    url(r'^$', 'hmates.views.invite_search', name='invite_search'),
)
