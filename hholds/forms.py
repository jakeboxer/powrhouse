from django import forms
from django.utils.translation import ugettext_lazy as _
from hholds.models import Household

class HouseholdForm (forms.ModelForm):
    
    class Meta:
        model = Household
