from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from hmates.models import Housemate
from top_notices.models import TopNoticeSlug, TopNoticeClosing

def top_notices_close (request, slug, hmate_pk):
    # Find the top notice and the housemate
    top_notice = get_object_or_404(TopNoticeSlug, slug=slug)
    hmate      = get_object_or_404(Housemate, pk=int(hmate_pk))
    
    # Close the top notice for the housemate
    TopNoticeClosing.objects.create(top_notice=top_notice, hmate=hmate)
    
    return HttpResponse("success", mimetype="text/plain")
