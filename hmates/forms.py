from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.core.mail import send_mail
from registration.forms import RegistrationFormUniqueEmail
from configoptions.models import ConfigOption
from hmates.models import Housemate, Invite
from random import choice
import string

def get_uname_from_email (email):
    """
    Return a munged email address that's fit to be a username
    """
    import re
    return re.sub(r"[^a-zA-Z0-9]+", "", email)[:30]

def get_normalized_username (user):
    return "u%d" % user.pk

def get_random_password (length):
    valid_chars = string.letters + string.digits
    return "".join([choice(valid_chars) for i in xrange(length)])

def create_user (username, email, first_name, last_name, pw):
    # Create the user
    user = User(username=username, email=email, first_name=first_name,
        last_name=last_name, is_active=True)
    
    # Set his/her password
    user.set_password(pw)
    
    # Save the user
    user.save()
    
    return user

def send_user_added_email (hmate, pw, adder):
    site = Site.objects.get_current()
    
    subj    = _("You've been registered for %s!") % site.name
    tpl     = get_template("hmates/add_email.txt")
    context = Context({
        "adder": adder,
        "hmate": hmate,
        "password": pw,
        "site": site
    })
    send_mail(subj, tpl.render(context), "noreply@powrhouse.net",
        [hmate.user.email])

attrs_dict = { 'class': 'required' }

class NumberOfHousematesForm (forms.Form):
    num_hmates = forms.IntegerField()

class HousemateForm (forms.ModelForm):
    first_name = forms.CharField(label=_("First name"), max_length=255)
    last_name  = forms.CharField(label=_("Last name"), max_length=255)
    email    = forms.EmailField(label=_("E-mail"), max_length=255)
    
    class Meta:
        model   = Housemate
        exclude = ("user", "hhold")
    
    def __init__ (self, *args, **kwargs):
        super(HousemateForm, self).__init__(*args, **kwargs)
        
        # if there's an instance, the initial values for some fields should be
        # populated by the instance's user
        if self.instance:
            self._populate_from_user()
    
    def _populate_from_user (self):
        self.initial["email"]      = self.instance.user.email
        self.initial["first_name"] = self.instance.user.first_name
        self.initial["last_name"]  = self.instance.user.last_name
    
    def clean_email (self):
        email = self.cleaned_data["email"].strip().lower()

        # if the user changed her email, make sure it's not taken
        changed_email = email != self.instance.user.email
        dupe_email_ct = User.objects.filter(email__iexact=email).count()
        if changed_email and dupe_email_ct > 0:
            msg = "The email '%s' is already taken."
            raise forms.ValidationError(msg % email)

        return email
    
    def save (self, *args, **kwargs):
        self.instance.user.email      = self.cleaned_data["email"]
        self.instance.user.first_name = self.cleaned_data["first_name"]
        self.instance.user.last_name  = self.cleaned_data["last_name"]
        self.instance.user.save()
        return super(HousemateForm, self).save(*args, **kwargs)


class SmallHousemateForm (forms.Form):
    first_name = forms.CharField(label=_("First name"), max_length=255)
    last_name  = forms.CharField(label=_("Last name"), max_length=255)
    email      = forms.EmailField(label=_("E-mail"), max_length=255)
    
    def clean_email (self):
        email = self.cleaned_data["email"].strip().lower()
        
        # Make sure the email is unique
        if User.objects.filter(email__iexact=email).count() > 0:
            msg = "The address '%s' is already taken."
            raise forms.ValidationError(msg % email)
        
        return email
    
    def setup_new_user (self, hmate, adder):
        # set up the username and password
        email_uname = get_uname_from_email(self.cleaned_data["email"])
        pw = get_random_password(ConfigOption.vals.get(
            "starting_pw_length", type=int, default=10))
        
        # create and save the user
        hmate.user = create_user(email_uname, self.cleaned_data["email"],
            self.cleaned_data["first_name"], self.cleaned_data["last_name"], pw)
        hmate.user.username = get_normalized_username(hmate.user)
        hmate.user.save()
        
        # Send an email
        send_user_added_email(hmate, pw, adder)


class SmallHousemateAddForm (SmallHousemateForm):
    
    def save (self, adder):
        hmate = Housemate(hhold=adder.hhold)
        
        # Set the user up
        self.setup_new_user(hmate, adder)
        hmate.save()
        
        return hmate


class SmallHousemateEditForm (SmallHousemateForm):
    
    def __init__ (self, pk, *args, **kwargs):
        super(SmallHousemateEditForm, self).__init__(*args, **kwargs)
        self.instance = Housemate.objects.get(pk=int(pk))
        
        if not self.is_bound:
            self.initial["email"]      = self.instance.user.email
            self.initial["first_name"] = self.instance.user.first_name
            self.initial["last_name"]  = self.instance.user.last_name
        
    def clean_email (self):
        email = self.cleaned_data["email"].strip().lower()
        
        # run the normal email clean, but only if the user changed her email
        if email != self.instance.user.email:
            email = super(SmallHousemateEditForm, self).clean_email()

        return email
    
    def save (self, adder):
        if self.instance.user:
            # if there's already a set user, just update her info
            self.instance.user.email      = self.cleaned_data["email"]
            self.instance.user.first_name = self.cleaned_data["first_name"]
            self.instance.user.last_name  = self.cleaned_data["last_name"]
            self.instance.user.save()
        else:
            # otherwise, a new one needs to be created
            self.setup_new_user(self.instance, adder)
        
        self.instance.save()
        return self.instance


class HousemateRegForm (RegistrationFormUniqueEmail):
    # We only need this username field so that it doesn't show up in the form.
    # There's no danger in this, since we ignore and overwrite the value anyway
    username   = forms.CharField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(max_length=255)
    last_name  = forms.CharField(max_length=255)
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
        label=_(u'I have read and agree to the Terms of Service'),
        error_messages={
            'required': u"You must agree to the terms to register."
        })
    
    def clean_username (self):
        # allow any username cuz we're going to munge it anyway
        return self.cleaned_data["username"]
    
    def clean (self):
        # temporarily use a munged version of the email address for the username
        if "email" in self.cleaned_data:
            email_uname = get_uname_from_email(self.cleaned_data["email"])
            self.cleaned_data["username"] = email_uname
        
        return self.cleaned_data
        

    def save (self):
         user = super(HousemateRegForm, self).save()
         user.username   = get_normalized_username(user)
         user.first_name = self.cleaned_data["first_name"]
         user.last_name  = self.cleaned_data["last_name"]
         
         user.save()

         # Attach the user to a new Housemate
         hmate = Housemate.objects.create(user=user)

         return user

class HousemateEmailSearchForm (forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=30)
    
    def get_result (self, hhold):
        try:
            user = User.objects.get(email=self.cleaned_data["email"])
        except User.DoesNotExist:
            return None
        
        hmate = user.hmates.all()[0]
        
        # see if there are any invites for the housemate, in the current
        # household
        invites = Invite.objects.filter(invitee=hmate, hhold=hhold)
        
        return hmate if invites.count() < 1 else None
