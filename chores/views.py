from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.core.mail import send_mail
from chores.forms import ChoreForm
from hmates.models import Housemate
from chores.models import Assignment

def send_emails (assign):
    """
    Sends any email notifications called for based on the state of the
    assignment.
    
    @param: assign Assignment to send emails based on
    """
    # if the hmate who completed the assignment wasn't the one who it was
    # assigned to, send an email to the person it was assigned to
    if assign.assigned_to != assign.done_by:
        from django.contrib.sites.models import Site
        subj = u"%s has done %s for you" \
            % (assign.done_by.get_full_name(), assign.chore.name)
        tpl     = get_template("assigns/done_by_other_email.txt")
        context = Context({"assign": assign,
            "site": Site.objects.get_current()})
        send_mail(subj, tpl.render(context), "noreply@powrhouse.net",
            [assign.assigned_to.user.email])
    

@login_required
def add (request):
    if request.method == "POST":
        form = ChoreForm(request.POST)
        
        if form.is_valid():
            chore = form.save(commit=False)
            chore.hhold = request.hmate.hhold
            chore.save()
            return redirect(chore)
    else:
        form = ChoreForm()
    
    return render_to_response(
        "chores/add.html", {"form": form},
        context_instance=RequestContext(request))

@login_required
def assign_done (request, object_id):
    # get the assignment
    assign = get_object_or_404(Assignment, pk=int(object_id))
    
    # make sure the housemate is in the same household as the chore
    if request.hmate.hhold != assign.chore.hhold:
        raise Http404
    
    # finish the assignment
    if not assign.is_done():
        assign.complete(request.hmate)
        send_emails(assign)
    
    return redirect("my_chores")

def assign_done_no_login (request, object_id, hmate_id, key):
    # get the assignment
    assign = get_object_or_404(Assignment, pk=int(object_id))
    
    # make sure the assignment's url key matches the passed key
    if key != assign.url_key: raise Http404
    
    # get the housemate
    hmate = get_object_or_404(Housemate, pk=int(hmate_id))
    
    # make sure the housemate is in the same household as the chore
    if hmate.hhold != assign.chore.hhold: raise Http404
    
    # finish the assignment
    if not assign.is_done():
        assign.complete(hmate)
        send_emails(assign)
    
    return render_to_response(
        "assigns/done_no_login.html", {"assign": assign, "hmate": hmate},
        context_instance=RequestContext(request))