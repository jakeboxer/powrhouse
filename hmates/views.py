from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.core.mail import send_mail
from django.forms.formsets import formset_factory
from configoptions.models import ConfigOption
from hmates.forms import HousemateForm, SmallHousemateAddForm,\
    SmallHousemateEditForm, HousemateEmailSearchForm, send_user_added_email,\
    get_random_password
from hmates.decorators import target_must_be_inactive, target_must_be_active,\
    target_cant_have_logged_in, must_live_together, target_must_be_user,\
    must_be_invitee
from hholds.decorators import must_have_hhold, target_cant_have_hhold
from hmates.models import Housemate, Invite
import datetime

@login_required
def me_edit (request):
    context = RequestContext(request)
    curr_hmate = context["curr_hmate"]
    
    if request.method == "POST":
        form = HousemateForm(request.POST, request.FILES, instance=curr_hmate)
        
        if form.is_valid():
            # if the form is valid, save and redirect
            form.save()
            return redirect("me")
    else:
        form = HousemateForm(instance=curr_hmate)
    
    return render_to_response(
        "me/edit.html", {"form": form}, context_instance=context)

@permission_required("hmates.add_housemate")
@login_required
def add_multiple (request, num_hmates):
    context    = RequestContext(request)
    hhold      = context["curr_hmate"].hhold
    num_hmates = int(num_hmates)
    SmallHousemateAddFormSet = formset_factory(SmallHousemateAddForm,
        extra=num_hmates)

    if request.method == "POST":
        fset = SmallHousemateAddFormSet(request.POST)

        if fset.is_valid():
            # Save every housemate if theyre all valid
            for form in fset.forms: form.save(context["curr_hmate"])
            return redirect("my_hhold")
    else:
        fset = SmallHousemateAddFormSet()

    return render_to_response(
        "hmates/add.html", {"fset": fset, "num_hmates": num_hmates},
        context_instance=context)

@login_required
def num (request):
    if request.method != "POST" or "num_hmates" not in request.POST:
        raise Http404

    try:
        num_hmates = int(request.POST["num_hmates"])
    except ValueError: raise Http404

    if request.method == "POST" and "num_hmates" in request.POST:
        return redirect("hmate_add_multiple", num_hmates=num_hmates)

    # If we've made it this far, it means we didn't redirect, so something's
    # wrong with the request
    raise Http404

@permission_required("hmates.edit_housemate")
@target_cant_have_logged_in
@must_live_together
def edit_inactive (request, object_id):
    context  = RequestContext(request)
    hmate_id = int(object_id)

    if request.method == "POST":
        form = SmallHousemateEditForm(hmate_id, request.POST)

        if form.is_valid():
            hmate = form.save(context["curr_hmate"])
            return redirect(hmate)
    else:
        form = SmallHousemateEditForm(hmate_id)

    return render_to_response(
        "hmates/edit.html", {"form": form}, context_instance=context)

@permission_required("hmates.add_housemate")
@target_cant_have_logged_in
@target_must_be_active
@must_live_together
def resend_add_email (request, object_id):
    context = RequestContext(request)
    
    # Find the housemate
    hmate = get_object_or_404(Housemate, pk=int(object_id))
    
    # Reset her password
    pw = get_random_password(ConfigOption.vals.get(
        "starting_pw_length", type=int, default=10))
    hmate.user.set_password(pw)
    hmate.user.save()
    
    # Send her a new email
    send_user_added_email(hmate, pw, context["curr_hmate"])
    
    # Set the message to be shown to the user
    msg = u"A new registration email has been sent to %s." \
        % hmate.get_full_name()
    context["user"].message_set.create(message=msg)
    
    return redirect("my_hhold")

@permission_required("hmates.delete_housemate")
@must_live_together
def boot (request, object_id):
    context = RequestContext(request)
    curr_hmate = context["curr_hmate"]
    
    # Find the housemate
    hmate = get_object_or_404(Housemate, pk=int(object_id))
    
    # If we've got a POST request, boot her
    if request.method == "POST":
        msg = u"%s was successfully booted from your household." \
            % hmate.get_full_name()
        
        if hmate.user:
            # if she has a user, save her and send an email
            subj    = u"You've been booted from %s" % curr_hmate.hhold
            tpl     = get_template("hmates/booted_email.txt")
            email_context = Context({"hmate": hmate})
            send_mail(subj, tpl.render(email_context),
                "noreply@powrhouse.net", [hmate.user.email])
            
            hmate.hhold = None
            hmate.save()
        else:
            hmate.delete() # otherwise, delete her
        
        context["user"].message_set.create(message=msg)
        
        return redirect("my_hhold")
    
    # Otherwise, we want confirmation
    return render_to_response(
        "hmates/confirm_boot.html", {"hmate": hmate}, context_instance=context)

@permission_required("hmates.add_housemate")
@must_have_hhold
def invite_search (request):
    value_dict = {}
    
    if request.method == "GET" and "email" in request.GET:
        value_dict["form"] = HousemateEmailSearchForm(request.GET)
        
        if value_dict["form"].is_valid():
            value_dict["searched"] = True
            value_dict["hmate"]    = value_dict["form"].get_result()
    else:
        value_dict["form"] = HousemateEmailSearchForm()
    
    return render_to_response("invites/search.html", value_dict,
        context_instance=RequestContext(request))

@permission_required("hmates.add_housemate")
@target_cant_have_hhold
@target_must_be_user
@must_have_hhold
def invite (request, object_id):
    context = RequestContext(request)
    
    # Get the housemates in question
    curr_hmate = context["curr_hmate"]
    hmate      = get_object_or_404(Housemate, pk=int(object_id))
    
    # make the invite
    invite = Invite.objects.create(inviter=curr_hmate, invitee=hmate,
        hhold=curr_hmate.hhold)
    
    # send an email to the invitee
    subj    = u"You've been invited to %s" % curr_hmate.hhold
    tpl     = get_template("invites/invited_email.txt")
    email_context = Context({"hmate": hmate, "curr_hmate": curr_hmate})
    send_mail(subj, tpl.render(email_context),
        "noreply@powrhouse.net", [hmate.user.email])
    
    return redirect("my_hhold")

@must_be_invitee
def invite_accept (request, object_id):
    # get the invite
    invite = get_object_or_404(Invite, pk=int(object_id))
    
    # put the housemate in the household and remove write permissions
    context = RequestContext(request)
    hhold   = invite.hhold
    context["curr_hmate"].hhold = hhold
    context["curr_hmate"].prevent_changes()
    context["curr_hmate"].save()
    
    # delete the invitation and redirect to her new household
    invite.delete()
    return redirect("hhold_branch")

@must_be_invitee
def invite_decline (request, object_id):
    # get the invite
    invite = get_object_or_404(Invite, pk=int(object_id))
    
    # set the invite to declined
    invite.declined = datetime.datetime.utcnow()
    invite.save()
    
    return redirect("hhold_branch")