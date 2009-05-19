from hholds.models import Household
from hholds.timezones import get_tzids_by_local_hour
from autoassign.classes import ChoreScheduler
import datetime

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
