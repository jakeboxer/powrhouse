from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.views.generic.simple import direct_to_template
from hmates.forms import HousemateRegForm
from registration.views import register
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    
    # for django-registration
    url(r'^accounts/register/$', register, {'form_class': HousemateRegForm}, 
        name='registration_register'),
    (r'^accounts/', include('registration.urls')),
    
    # password reset
    url(r'^password/forgot/$', password_reset,
        {'email_template_name': 'registration/password_reset_email.txt'}, 
        "pw_reset"),
        url(r'^password/forgot/confirm/(?P<uidb36>[0-9]+)/(?P<token>[-0-9A-Za-z]+)/',
        password_reset_confirm, name="pw_reset_confirm"),
    
    url(r'^me/', include('hmates.me_urls')),
    url(r'^household/', include('hholds.urls')),
    url(r'^housemate/', include('hmates.urls')),
    url(r'^invite/', include('hmates.invite_urls')),
    url(r'^chore/', include('chores.urls')),
    url(r'^topnotices/', include('top_notices.urls')),
    url(r'^prototype/add_hmate_success/$', direct_to_template,
        {"template": "prototypes/add_hmates_success.html"})
)
