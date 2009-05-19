import datetime, pytz

TZ_CHOICES = [
    "US/Alaska", 
    "US/Aleutian", 
    "US/Arizona", 
    "US/Central", 
    "US/East-Indiana", 
    "US/Eastern", 
    "US/Hawaii", 
    "US/Indiana-Starke", 
    "US/Michigan", 
    "US/Mountain", 
    "US/Pacific", 
    "US/Pacific-New", 
    "US/Samoa"
]

def get_choices_tuple ():
    return tuple([(i+1, TZ_CHOICES[i]) for i in xrange(len(TZ_CHOICES))])

def get_tz_by_id (tz_id):
    return TZ_CHOICES[tz_id - 1]

def get_id_by_tz (tz):
    return TZ_CHOICES.index(tz) + 1

def tz_has_target_hr (tz, curr_utc_dt, hr):
    """
    Returns whether or not the passed timezone has the target hour at the
    specified UTC time.
    
    @param: tz Timezone to check
    @param: curr_utc_dt datetime to use
    @param: hr Hour to see if we've matched
    """
    return pytz.timezone(tz).fromutc(curr_utc_dt).hour == hr

def get_tzids_by_local_hour (hr, dt=datetime.datetime.utcnow()):
    """
    Returns a list of all the IDs of timezones whose hour (at the specified
    time) match the specified hour.
    
    @param: hr Hour to find matches on
    @param: dt UTC datetime to look at on the timezones (defaults to now)
    """
    tzs = TZ_CHOICES
    # Go through every timezone in the list. If it's currently the target
    # hour in that timezone, put the timezone's id in the list
    return [get_id_by_tz(tz) for tz in tzs if tz_has_target_hr(tz, dt, hr)]
        