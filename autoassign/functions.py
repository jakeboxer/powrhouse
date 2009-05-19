from django.template import Context
from django.template.loader import get_template
from django.core.mail import send_mail
from hholds.models import Household
from hholds.timezones import get_tzids_by_local_hour
from autoassign.classes import ChoreScheduler
import datetime

MORNING_HR = 0
EVENING_HR = 20

def get_hholds_by_local_hr (hr, dt=datetime.datetime.utcnow()):
    """
    Returns all the households who locally (based on timezone) have the
    specified hour.
    
    @param: hr Hour that the matching households should have
    @param: dt Datetime to check on (defaults to now)
    """
    tzids = get_tzids_by_local_hour(hr, dt)
    return Household.objects.filter(timezone_id__in=tzids)

def get_chore_assignments (hhold):
    return ChoreScheduler(hhold).get_assignments()

def assign_chores (assign_set):
    """
    Assigns the chores as suggested by the specified assignment set
    
    @param: assign_set Dictionary (key=housemate, value=list of chores)
        specifying which chores should be assigned to which housemates
    """
    for hmate in assign_set:
        for chore in assign_set[hmate]:
            chore.assign_to(hmate)

def morning_digest_subj (hmate):
    """
    Create a subject line for the morning digest email
    
    @param: hmate Housemate to get the subject line for
    """
    num_chores = hmate.get_incomplete_assigns().count()
    today      = hmate.hhold.get_local_datetime()
    date_str   = "%d/%d" % (today.month, today.day)
    
    if num_chores == 0:
        subj = "You have no chores today (%s)" % date_str
    elif num_chores == 1:
        subj = "You have one chore today (%s)" % date_str
    else:
        subj = "You have %d chores today (%s)" % (num_chores, date_str)
    
    return subj

def morning_digest_body (hmate):
    """
    Create a body for the morning digest email
    
    @param: hmate Housemate to get the body for
    """
    context = Context({"hmate": hmate})
    return get_template("digest/morning_body.txt").render(context)

def send_morning_digest (hhold):
    """
    Sends a digest email (intended for the morning) to all members of the
    specified household
    
    @param: hhold Household containing members to send the digest to
    """
    # Assign all the chores that should be assigned
    assign_chores(get_chore_assignments(hhold))
    
    # Send the digest email to each member of the household
    for hmate in hhold.hmates.all():
        subj = morning_digest_subj(hmate)
        body = morning_digest_body(hmate)
        send_mail(subj, body, "noreply@powrhouse.net", [hmate.user.email])
    
def send_evening_digest (hhold):
    raise NotImplementedError

def send_morning_digests ():
    """
    Sends the morning digest email to all households (for whom it is morning)
    """
    send_digests(MORNING_HR, send_morning_digest)

def send_evening_digests ():
    """
    Sends the evening digest email to all households (for whom it is evening)
    """
    send_digests(EVENING_HR, send_evening_digest)

def send_digests (hr, digest_fn):
    """
    Calls the specified digest-sending function on all households who, based on
    their timezone, are in the specified hour.
    """
    for hhold in get_hholds_by_local_hr(hr):
        digest_fn(hhold)