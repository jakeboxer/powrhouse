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
