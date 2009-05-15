from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.core.mail import send_mail
from hholds.forms import HouseholdForm
from hholds.decorators import cannot_have_hhold, must_have_hhold

@login_required
def hhold_branch (request):
    context = RequestContext(request)
    url_name = "my_hhold" if context["curr_hmate"].hhold else "hhold_create"
    
    return redirect(url_name)

@permission_required("hholds.change_household")
@login_required
def edit (request):
    context = RequestContext(request)
    hhold   = context["curr_hmate"].hhold
    
    if request.method == "POST":
        form = HouseholdForm(request.POST, request.FILES, instance=hhold)
        
        if form.is_valid():
            # if the form is valid, save and redirect
            hhold = form.save()
            return redirect("my_hhold")
    else:
        form = HouseholdForm(instance=hhold)
    
    return render_to_response(
        "hholds/edit.html", {"form": form}, context_instance=context)

@cannot_have_hhold
def create (request):
    context = RequestContext(request)
    
    if request.method == "POST":
        form = HouseholdForm(request.POST, request.FILES)
        
        if form.is_valid():
            # if the form is valid
            hhold = form.save()
            
            # attach the housemate to the household
            context["curr_hmate"].hhold = hhold
            context["curr_hmate"].allow_changes()
            context["curr_hmate"].save()
            
            return redirect("my_hhold")
    else:
        form = HouseholdForm()
    
    return render_to_response(
        "hholds/create.html", {"form": form}, context_instance=context)

@must_have_hhold
def leave (request):
    context = RequestContext(request)
    curr_hmate = context["curr_hmate"]
    
    if request.method == "POST":
        # Remove the housemate from the household
        hhold = curr_hmate.hhold
        curr_hmate.hhold = None
        curr_hmate.save()
        
        if hhold.hmates.count() > 0:
            # Send an email to all the remaining housemates
            subj    = u"%s has left your household" % curr_hmate.get_full_name()
            tpl     = get_template("hholds/left_email.txt")
            email_context = Context({"hmate": curr_hmate, "hhold": hhold})
            send_mail(subj, tpl.render(email_context), "noreply@powrhouse.net",
                zip(*hhold.hmates.values_list("user__email"))[0])
        else:
            # if there are no remaining housemates, delete the household
            hhold.delete()
        
        return redirect("hhold_branch")
    
    return render_to_response("hholds/leave.html", context_instance=context)
            