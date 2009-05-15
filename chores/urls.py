from django.conf.urls.defaults import *
from django.template import RequestContext
from django.views.generic.list_detail import object_detail
from django.views.generic.create_update import update_object, delete_object
from django.contrib.auth.decorators import login_required, permission_required
from chores.models import Chore
from chores.forms import ChoreForm
from chores.decorators import must_own_chore

chore_detail_dict = {
    "queryset":             Chore.objects.all(),
    "template_name":        "chores/detail.html",
    "template_object_name": "chore"
}

chore_edit_dict = {
    "form_class":           ChoreForm,
    "post_save_redirect":   "/chore/%(id)s",
    "template_name":        "chores/edit.html",
    "template_object_name": "chore"
}

chore_delete_dict = {
    "model":                Chore,
    "post_delete_redirect": "/household/",
    "template_object_name": "chore",
    "template_name":        "chores/confirm_delete.html"
}


urlpatterns = patterns('',
    url(r'^assignment/', include('chores.assign_urls')),
    # Assignments
    url(r'^assignment/(?P<object_id>[0-9]+)/done/(?P<hmate_id>[0-9]+)/$',
        'chores.views.assign_done', name="assign_done"),
    
    # Chore
    url(r"^(?P<object_id>[0-9]+)/$", must_own_chore(object_detail),
        chore_detail_dict, name="chore_detail"),
    url(r"^add/$", "chores.views.add", name="chore_add"),
    url(r"^(?P<object_id>[0-9]+)/edit/$", 
        permission_required("chores.change_chore")(\
            must_own_chore(update_object)),
        chore_edit_dict, name="chore_edit"),
    url(r"^(?P<object_id>[0-9]+)/delete/$",
        permission_required("chores.delete_chore")(\
            must_own_chore(delete_object)),
        chore_delete_dict, name="chore_delete"),
)
