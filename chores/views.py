from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from chores.forms import ChoreForm
from hmates.models import Housemate
from chores.models import Assignment

@login_required
def add (request):
    context = RequestContext(request)
    
    if request.method == "POST":
        form = ChoreForm(request.POST)
        
        if form.is_valid():
            chore = form.save(commit=False)
            chore.hhold = context["curr_hmate"].hhold
            chore.save()
            return redirect(chore)
    else:
        form = ChoreForm()
    
    return render_to_response(
        "chores/add.html", {"form": form}, context_instance=context)

@login_required
def assign_done (request, object_id):
    context = RequestContext(request)
    
    # get the assignment
    assign = get_object_or_404(Assignment, pk=int(object_id))
    
    # make sure the housemate is in the same household as the chore
    if context["curr_hmate"].hhold != assign.chore.hhold: raise Http404
    
    # finish the assignment
    if not assign.is_done(): assign.complete(context["curr_hmate"])
    
    return redirect("my_day")

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
    if not assign.is_done(): assign.complete(hmate)
    
    return render_to_response(
        "assigns/done_no_login.html", {"assign": assign, "hmate": hmate},
        context_instance=RequestContext(request))