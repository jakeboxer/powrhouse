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
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^\w+$',
        error_message=_("This value must contain only letters, numbers and \
        underscores."))
    email    = forms.EmailField(label=_("E-mail"), max_length=255)
    
    class Meta:
        model   = Housemate
        exclude = ("user", "hhold", "username_changed")
    
    def __init__ (self, *args, **kwargs):
        super(HousemateForm, self).__init__(*args, **kwargs)
        
        # if there's an instance, the initial values for some fields should be
        # populated by the instance's user
        if self.instance: self._populate_from_user()
    
    def _populate_from_user (self):
        user = self.instance.user
        self.initial["username"]   = user.username
        self.initial["email"]      = user.email
        self.initial["first_name"] = user.first_name
        self.initial["last_name"]  = user.last_name
    
    def clean_username (self):
        uname = self.cleaned_data["username"].strip().lower()

        # if the user changed her username, make sure it's not taken
        new_uname   = uname != self.instance.user.username
        dupe_unames = User.objects.filter(username__iexact=uname)
        if new_uname and dupe_unames.count() > 0:
            msg = "The username '%s' is already taken."
            raise forms.ValidationError(msg % uname)

        return uname
    
    def clean_email (self):
        email = self.cleaned_data["email"].strip().lower()

        # if the user changed her email, make sure it's not taken
        new_email   = email != self.instance.user.email
        dupe_emails = User.objects.filter(email__iexact=email)
        if new_email and dupe_emails.count() > 0:
            msg = "The email '%s' is already taken."
            raise forms.ValidationError(msg % email)

        return email
    
    def save (self, *args, **kwargs):
        self.instance.user.username   = self.cleaned_data["username"]
        self.instance.user.email      = self.cleaned_data["email"]
        self.instance.user.first_name = self.cleaned_data["first_name"]
        self.instance.user.last_name  = self.cleaned_data["last_name"]
        self.instance.user.save()
        return super(HousemateForm, self).save(*args, **kwargs)


class SmallHousemateForm (forms.Form):
    first_name = forms.CharField(label=_("First name"), max_length=255)
    last_name  = forms.CharField(label=_("Last name"), max_length=255)
    username   = forms.CharField(label=_("Username"), max_length=255,
        required=False)
    email      = forms.CharField(label=_("E-mail"), max_length=255,
        required=False)
    
    
    def clean_username (self):
        username = self.cleaned_data["username"].strip().lower()
        ct       = User.objects.filter(username__iexact=username).count()
        
        # Make sure the username, if it exists, is unique
        if username and (ct > 0):
            msg = "The username '%s' is already taken."
            raise forms.ValidationError(msg % username)
        
        return username
    
    def clean_email (self):
        email = self.cleaned_data["email"].strip().lower()
        ct    = User.objects.filter(email__iexact=email).count()
        
        # Make sure the email, if it exists, is unique
        if email and (ct > 0):
            msg = "The address '%s' is already taken."
            raise forms.ValidationError(msg % email)
        
        return email
    
    def clean (self):
        has_uname = "username" in self.cleaned_data
        has_email = "email" in self.cleaned_data
        valid_uname = has_uname and self.cleaned_data["username"]
        valid_email = has_email and self.cleaned_data["email"]
        valid_user = valid_uname and valid_email
        
        # make sure that there's either an email AND username, or neither
        if valid_uname and not valid_email:
            msg = "If a housemate has a username, he/she needs an email."
            raise forms.ValidationError(msg)
        elif valid_email and not valid_uname:
            msg = "If a housemate has an email, he/she needs a username."
            raise forms.ValidationError(msg)
        
        return self.cleaned_data
    
    def setup_new_user (self, hmate, adder):
        pw = get_random_password(ConfigOption.vals.get(
            "starting_pw_length", type=int, default=10))
        hmate.user = create_user(self.cleaned_data["username"],
            self.cleaned_data["email"], self.cleaned_data["first_name"], 
            self.cleaned_data["last_name"], pw)
        
        # Send an email
        send_user_added_email(hmate, pw, adder)


class SmallHousemateAddForm (SmallHousemateForm):
    
    def save (self, adder):
        hmate = Housemate(hhold=adder.hhold)
        
        if "username" in self.cleaned_data and self.cleaned_data["username"]:
            # If a username was provided, set the user up
            self.setup_new_user(hmate, adder)
        else:
            # If no username was provided, just save the first and last name
            hmate.first_name = self.cleaned_data["first_name"]
            hmate.last_name  = self.cleaned_data["last_name"]
        
        hmate.save()
        
        return hmate


class SmallHousemateEditForm (SmallHousemateForm):
    
    def __init__ (self, pk, *args, **kwargs):
        super(SmallHousemateEditForm, self).__init__(*args, **kwargs)
        self.instance = Housemate.objects.get(pk=int(pk))
        
        if not self.is_bound:
            if self.instance.user:
                self.initial["username"]   = self.instance.user.username
                self.initial["email"]      = self.instance.user.email
                self.initial["first_name"] = self.instance.user.first_name
                self.initial["last_name"]  = self.instance.user.last_name
            else:
                self.initial["first_name"] = self.instance.first_name
                self.initial["last_name"]  = self.instance.last_name
    
    def clean_username (self):
        username = self.cleaned_data["username"].strip().lower()
        
        # run the normal username clean, but only if the user changed her
        # username
        if self.instance.user and username != self.instance.user.username:
            username = super(SmallHousemateEditForm, self).clean_username()
        
        return username
        
    def clean_email (self):
        email = self.cleaned_data["email"].strip().lower()
        
        # run the normal email clean, but only if the user changed her email
        if self.instance.user and email != self.instance.user.email:
            email = super(SmallHousemateEditForm, self).clean_email()

        return email
    
    def clean (self):
        if self.instance.user:
            user = self.instance.user
            
            has_username   = "username" in self.cleaned_data
            empty_username = has_username and not self.cleaned_data["username"]
            has_email      = "email" in self.cleaned_data
            empty_email    = has_email and not self.cleaned_data["email"]
            
            # make sure they didn't try to remove an existing username
            if user.username and empty_username:
                msg = "You cannot remove your housemate's existing username (but you can change it)."
                raise forms.ValidationError(msg)
        
            # make sure they didn't try to remove an existing email
            if user.email and empty_email:
                msg = "You cannot remove your housemate's existing email (but you can change it)."
                raise forms.ValidationError(msg)
        
        return super(SmallHousemateEditForm, self).clean()
    
    def save (self, adder):
        user = self.instance.user
        
        uname_exists = "username" in self.cleaned_data
        email_exists = "email" in self.cleaned_data
        uname_set    = uname_exists and self.cleaned_data["username"]
        email_set    = email_exists and self.cleaned_data["email"]
        
        if uname_set and email_set:
            if user:
                # if there's already a set user, just update her info
                user.username   = self.cleaned_data["username"]
                user.email      = self.cleaned_data["email"]
                user.first_name = self.cleaned_data["first_name"]
                user.last_name  = self.cleaned_data["last_name"]
                user.save()
            else:
                # otherwise, a new one needs to be created
                self.setup_new_user(self.instance, adder)
        else:
            # if no username/email was set, just update the housemate
            self.instance.first_name = self.cleaned_data["first_name"]
            self.instance.last_name  = self.cleaned_data["last_name"]
        
        self.instance.save()
        return self.instance


class HousemateRegForm (RegistrationFormUniqueEmail):
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
