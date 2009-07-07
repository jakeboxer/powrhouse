from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

INTERVAL_CHOICES = (
    (1, _('Every day')),
    (2, _('Every other day')),
    (3, _('Every 3 days')),
    (7, _('Every week')),
    ('other', _('Other')),
)

class IntervalInput (forms.Widget):
    
    def render (self, name, value, attrs={}):
        if value is None: value = "1"
        
        select_box = forms.Select(choices=INTERVAL_CHOICES)
        text_box   = forms.TextInput()
        other_text = _("""
        <div id="id_%s_other">Every %s day(s).</div>
        """) % (name, text_box.render(u"%s_other" % name, value))
        
        return mark_safe(u'%s %s' % (select_box.render(name, value, attrs),
            other_text))
        