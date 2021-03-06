from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from hholds.decorators import cannot_have_hhold, hhold_required
from hholds.forms import HouseholdForm

@login_required
def hhold_branch (request):
    if request.hmate.hhold:
        url_name = "my_hhold"
    else:
        url_name = "hhold_create"
    
    return HttpResponseRedirect(reverse(url_name))

@login_required
@hhold_required
def edit (request):
    hhold   = request.hmate.hhold
    
    if request.method == "POST":
        form = HouseholdForm(request.POST, request.FILES, instance=hhold)
        
        if form.is_valid():
            # if the form is valid, save and redirect
            hhold = form.save()
            return HttpResponseRedirect(reverse("my_hhold"))
    else:
        form = HouseholdForm(instance=hhold)
    
    return render_to_response(
        "hholds/edit.html", {"form": form}, 
        context_instance=RequestContext(request))

@login_required
@cannot_have_hhold
def create (request):
    if request.method == "POST":
        form = HouseholdForm(request.POST, request.FILES)
        
        if form.is_valid():
            # if the form is valid
            hhold = form.save()
            
            # attach the housemate to the household
            request.hmate.hhold = hhold
            request.hmate.save()
            
            return HttpResponseRedirect(reverse("my_hhold"))
    else:
        form = HouseholdForm()
    
    return render_to_response(
        "hholds/create.html", {"form": form},
        context_instance=RequestContext(request))

@login_required
@hhold_required
def leave (request):
    curr_hmate = request.hmate
    
    if request.method == "POST":
        # Remove the housemate from the household
        hhold = curr_hmate.hhold
        curr_hmate.hhold = None
        curr_hmate.save()
        
        if hhold.hmates.count() > 0:
            site = Site.objects.get_current()
            
            # Send an email to all the remaining housemates
            subj    = u"%s has left your household" % curr_hmate.get_full_name()
            tpl     = get_template("hholds/left_email.txt")
            context = Context({"hmate": curr_hmate, "hhold": hhold,
                "site": site})
            send_mail(subj, tpl.render(context),
                "noreply@powrhouse.net",
                hhold.hmates.values_list("user__email", flat=True))
        else:
            # if there are no remaining housemates, delete the household
            hhold.delete()
        
        return HttpResponseRedirect(reverse("hhold_branch"))
    
    return render_to_response("hholds/leave.html",
        context_instance=RequestContext(request))
