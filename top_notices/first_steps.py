from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

def has_hhold (hmate):
    return bool(hmate.hhold)

def has_hmates (hmate):
    return bool(hmate.hhold) and hmate.hhold.hmates.count() > 1

def has_chores (hmate):
    return bool(hmate.hhold) and hmate.hhold.chores.count() > 0


class _SingleStep (object):
    msg       = ""
    done      = False
    prev_step = None
    
    def __init__ (self, msg, done, prev_step = None):
        self.msg       = msg
        self.done      = done
        self.prev_step = prev_step
    
    def is_upcoming (self):
        """
        Returns whether or not there are steps to be completed before this one
        """
        print self.prev_step is not None
        return self.prev_step is not None and not self.prev_step.done
    
    def __unicode__ (self):
        """
        
        """
        if self.done:
            class_name = "done"
        elif self.is_upcoming():
            class_name = "upcoming"
        else:
            class_name = ""
        
        return u'<li class="%s">%s</li>' % (class_name, self.msg)


def get_first_steps (hmate):
    steps = []
    
    # step 1
    step1_done = has_hhold(hmate)
    step1_msg  = "Create your household."
    if step1_done:
        step1_msg = 'Step 1: Create your household.'
    else:
        step1_msg = 'Step 1: <a href="%s">Create your household</a>.' \
            % reverse("hhold_create")
    steps.append(_SingleStep(step1_msg, step1_done))
    
    # step 2
    step2_done = has_hmates(hmate)
    if step2_done or not step1_done or not steps[-1].done:
        step2_msg = "Step 2: Add a housemate to your household."
    else:
        step2_msg = '''Step 2: <a href="%s">Add a housemate</a> to your 
            household.''' % reverse("hmate_add")
    steps.append(_SingleStep(step2_msg, step2_done, steps[-1]))
    
    # step 3
    step3_done = has_chores(hmate)
    if step3_done or not step1_done or not steps[-1].done:
        step3_msg = "Step 3: Set up a chore."
    else:
        step3_msg = 'Step 3: <a href="%s">Set up a chore.</a>' \
            % reverse("chore_add")
    steps.append(_SingleStep(step3_msg, step3_done, steps[-1]))
    
    # step 4
    if not step1_done or not steps[-1].done:
        hhold_txt = "My Household page"
    else:
        hhold_txt = '<a href="%s">My Household page</a>' \
            % reverse("my_hhold")
        
    step3_msg = """Step 4: That's it! At midnight, PowrHouse will send emails to 
        you and your housemate(s), telling each of you what chores to do. If you 
        have any more housemates or chores to add, you can do it on the %s."""\
        % hhold_txt
    steps.append(_SingleStep(step3_msg, False, steps[-1]))
    
    return steps


class FirstSteps (object):
    steps = None
    
    def __init__ (self, hmate):
        self.steps = get_first_steps(hmate)
    
    def to_notice (self):
        str_steps = [unicode(step) for step in self.steps]
        return _("""<h2>OK, I'm in. What do I do now?</h2>
            <ul id="what_now">%s</ul>""") % u''.join(str_steps)
