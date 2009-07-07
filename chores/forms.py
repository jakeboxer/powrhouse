from django import forms
from django.utils.translation import ugettext_lazy as _
from chores.models import Chore, SECS_PER_DAY, DEFAULT_INTERVAL
    
class ChoreForm (forms.ModelForm):
    interval = forms.IntegerField(min_value=1, max_value=365)
    
    class Meta:
        model   = Chore
        exclude = ("hhold",)
    
    def __init__ (self, *args, **kwargs):
        super(ChoreForm, self).__init__(*args, **kwargs)
        
        if "interval" in self.initial:
            # if there's already an initial value, turn it from seconds to days
            self.initial["interval"] /= SECS_PER_DAY
        else:
            # if there's no initial value yet, take the one that there's going
            # to be and turn it from seconds to days
            self.initial["interval"] = DEFAULT_INTERVAL / SECS_PER_DAY
    
    def clean_interval (self):
        return str(int(self.cleaned_data["interval"]) * SECS_PER_DAY)