from chores.models import Chore, SECS_PER_DAY, DEFAULT_INTERVAL
from chores.widgets import IntervalInput
from django import forms
from django.utils.translation import ugettext_lazy as _

INTERVAL_CHOICES = (
    (1, _('Every day')),
    (2, _('Every other day')),
    (3, _('Every 3 days')),
    (7, _('Every week')),
    ('other', _('Other')),
)

class ChoreForm (forms.ModelForm):
    interval = forms.IntegerField(\
        label=_('How often should this chore be done?'), min_value=1,
        max_value=365, widget=forms.Select(choices=INTERVAL_CHOICES))
    
    class Meta:
        model   = Chore
        exclude = ("hhold",)
    
    def __init__ (self, *args, **kwargs):
        super(ChoreForm, self).__init__(*args, **kwargs)
        
        if "interval" in self.initial:
            # if there's already an initial value, turn it from seconds to days
            # and record it as a separate attribute
            days = self.initial["interval"] / SECS_PER_DAY
            self.fields["interval"].widget.attrs["original"] = days
            
            # if the number of days is in the presets, set the initial value to
            # the number of days. otherwise, set it to "other"
            if days in [c[0] for c in INTERVAL_CHOICES if c[0] != "other"]:
                self.initial["interval"] = days
            else:
                self.initial["interval"] = "other"
        else:
            # if there's no initial value yet, take the one that there's going
            # to be and turn it from seconds to days
            self.initial["interval"] = DEFAULT_INTERVAL / SECS_PER_DAY
            
            # there's no original value since it's new, so set it to blank
            self.fields["interval"].widget.attrs["original"] = ""
    
    def clean_interval (self):
        return str(int(self.cleaned_data["interval"]) * SECS_PER_DAY)