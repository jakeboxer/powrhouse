from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from hmates.models import Housemate
from top_notices.models import TopNoticeSlug, TopNoticeClosing

def top_notices_close (request, slug):
    # Find the top notice
    top_notice = get_object_or_404(TopNoticeSlug, slug=slug)
    
    # Close the top notice for the housemate
    TopNoticeClosing.objects.create(top_notice=top_notice, hmate=request.hmate)
    
    return HttpResponse("success", mimetype="text/plain")
