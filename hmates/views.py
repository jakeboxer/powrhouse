from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.views import password_change_done
from django.contrib.sites.models import Site
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.core.mail import send_mail
from django.forms.formsets import formset_factory
from configoptions.models import ConfigOption
from hmates.forms import HousemateForm, SmallHousemateAddForm,\
    SmallHousemateEditForm, HousemateEmailSearchForm, HousemateRegForm,\
    send_user_added_email, get_random_password
from hmates.decorators import target_must_be_inactive, target_must_be_active,\
    must_live_together
from hholds.decorators import hhold_required, target_cant_have_hhold
from hmates.models import Housemate, Invite
from recaptcha.client import captcha
from registration.views import register
import datetime

def index_branch (request):
    if request.hmate.is_anonymous():
        print("hey0")
        redir = HttpResponseRedirect("/home/")
    else:
        print('hey1')
        redir = HttpResponseRedirect(reverse("my_hhold"))
    
    return redir

@login_required
def me_edit (request):
    curr_hmate = request.hmate
    
    if request.method == "POST":
        form = HousemateForm(request.POST, request.FILES, instance=curr_hmate)
        
        if form.is_valid():
            # if the form is valid, save and redirect
            form.save()
            return HttpResponseRedirect(reverse("my_hhold"))
    else:
        form = HousemateForm(instance=curr_hmate)
    
    return render_to_response(
        "me/edit.html", {"form": form},
        context_instance=RequestContext(request))

@login_required
@hhold_required
def add (request):
    SmallHousemateAddFormSet = formset_factory(SmallHousemateAddForm,
        extra=100)

    if request.method == "POST":
        fset = SmallHousemateAddFormSet(request.POST)

        if fset.is_valid():
            # Save every housemate if theyre all valid. If an email address
            # appears in multiple forms, only create the first account
            emails = set([None])
            for form in fset.forms:
                if form.cleaned_data.get("email") not in emails:
                    form.save(adder=request.hmate)
                    emails.add(form.cleaned_data["email"])
            
            return HttpResponseRedirect(reverse("my_hhold"))
    else:
        fset = SmallHousemateAddFormSet()
    
    hmates = list(request.hmate.hhold.hmates.all())

    return render_to_response(
        "hmates/add.html", {"fset": fset, "hmates": hmates},
        context_instance=RequestContext(request))

@login_required
@must_live_together
def edit_inactive (request, object_id):
    hmate = get_object_or_404(Housemate, pk=int(object_id))
    
    # make sure the housemate hasn't logged in
    if hmate.has_logged_in():
        raise Http404

    if request.method == "POST":
        form = SmallHousemateEditForm(hmate.pk, request.POST)

        if form.is_valid():
            hmate = form.save(request.hmate)
            return HttpResponseRedirect(hmate.get_absolute_url())
    else:
        form = SmallHousemateEditForm(hmate.pk)

    return render_to_response(
        "hmates/edit.html", {"form": form},
        context_instance=RequestContext(request))

@login_required
@target_must_be_active
@must_live_together
def resend_add_email (request, object_id):
    # Find the housemate
    hmate = get_object_or_404(Housemate, pk=int(object_id))
    
    # make sure the housemate hasn't logged in
    if hmate.has_logged_in():
        raise Http404
    
    # Reset her password
    pw = get_random_password(ConfigOption.vals.get("starting_pw_length", 
        type=int, default=10))
    hmate.user.set_password(pw)
    hmate.user.save()
    
    # Send her a new email
    send_user_added_email(hmate, pw, request.hmate)
    
    # Set the message to be shown to the user
    msg = u"A new registration email has been sent to %s." \
        % hmate.get_full_name()
    request.user.message_set.create(message=msg)
    
    return HttpResponseRedirect(reverse("my_hhold"))

@login_required
@must_live_together
def boot (request, object_id):
    # Find the housemate
    hmate = get_object_or_404(Housemate, pk=int(object_id))
    
    # If we've got a POST request, boot her
    if request.method == "POST":
        msg = u"%s was successfully booted from your household." \
            % hmate.get_full_name()
        
        if hmate.has_logged_in():
            # if she has logged in, save her and send an email
            site = Site.objects.get_current()
            subj = u"You've been booted from %s" % request.hmate.hhold
            tpl  = get_template("hmates/booted_email.txt")
            email_context = Context({"hmate": hmate, "site": site})
            send_mail(subj, tpl.render(email_context), "noreply@powrhouse.net",
                [hmate.user.email])
            
            hmate.hhold = None
            hmate.save()
        else:
            # otherwise, delete her
            hmate.user.delete()
            hmate.delete()
        
        request.user.message_set.create(message=msg)
        
        return HttpResponseRedirect(reverse("my_hhold"))
    
    # Otherwise, we want confirmation
    return render_to_response(
        "hmates/confirm_boot.html", {"hmate": hmate},
        context_instance=RequestContext(request))

@login_required
@hhold_required
def invite_search (request):
    searched = False
    hmate    = None
    
    if request.method == "GET" and "email" in request.GET:
        form = HousemateEmailSearchForm(request.GET, searcher=request.hmate)
        
        if form.is_valid():
            searched = True
            hmate    = form.get_result()
    else:
        form = HousemateEmailSearchForm(searcher=request.hmate)
    
    return render_to_response("invites/search.html",
        {"form": form, "searched": searched, "hmate": hmate},
        context_instance=RequestContext(request))

@login_required
@target_cant_have_hhold
@hhold_required
def invite (request, object_id):
    # Get the housemates in question
    hmate = get_object_or_404(Housemate, pk=int(object_id))
    
    # make the invite
    invite = Invite.objects.create(inviter=request.hmate, invitee=hmate,
        hhold=request.hmate.hhold)
    
    # send an email to the invitee
    site = Site.objects.get_current()
    subj = _("You've been invited to %s") % request.hmate.hhold
    tpl  = get_template("invites/invited_email.txt")
    email_context = Context({"hmate": hmate, "curr_hmate": request.hmate,
        "site": site})
    send_mail(subj, tpl.render(email_context), "noreply@powrhouse.net",
        [hmate.user.email])
    
    # set a message
    msg = _("Successfully invited %s to your household.") % hmate
    request.user.message_set.create(message=msg)
    
    return HttpResponseRedirect(reverse("my_hhold"))

@login_required
def invite_accept (request, object_id):
    # get the invite
    invite = get_object_or_404(Invite, pk=int(object_id))
    
    # make sure the logged-in housemate is the invitee on the invite
    if invite.invitee != request.hmate:
        raise Http404
    
    # put the housemate in the household
    request.hmate.hhold = invite.hhold
    request.hmate.save()
    
    # delete the invitation and redirect to her new household
    invite.delete()
    return HttpResponseRedirect(reverse("hhold_branch"))

@login_required
def invite_decline (request, object_id):
    # get the invite
    invite = get_object_or_404(Invite, pk=int(object_id))
    
    # make sure the logged-in housemate is the invitee on the invite
    if invite.invitee != request.hmate:
        raise Http404
    
    # set the invite to declined
    invite.declined = datetime.datetime.utcnow()
    invite.save()
    
    return HttpResponseRedirect(reverse("hhold_branch"))

@login_required
def pw_edit_done (request):
    # record the time that the housemate's password was changed
    request.hmate.password_chosen = datetime.datetime.utcnow()
    request.hmate.save()
    
    # show the normal password changed view
    return password_change_done(request)

def custom_register (request, *args, **kwargs):
    """
    Wrap the django-registration register view in a custom view, so that we can
    use reCAPTCHA.
    """
    if request.method == "POST":
        # Check the captcha
        check_captcha = captcha.submit(\
            request.POST["recaptcha_challenge_field"],
            request.POST["recaptcha_response_field"],
            settings.RECAPTCHA_PRIVATE_KEY,
            request.META["REMOTE_ADDR"])
        
        if not check_captcha.is_valid:
            # If the captcha is wrong, error
            form    = kwargs["form_class"](request.POST)
            context = {"form": form, "recaptcha_failed": True}
            
            if "extra_context" in kwargs:
                context.update(kwargs["extra_context"])
            
            return render_to_response("registration/registration_form.html",
                context, context_instance=RequestContext(request))
        
    return register(request, *args, **kwargs)