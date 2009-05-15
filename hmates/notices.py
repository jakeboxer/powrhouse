
class Notice (object):
    """
    Adaptor to treat content (that implements the to_notice() method) like a
    notice.
    """
    
    def __init__ (self, content):
        self.content = content
    
    def __unicode__ (self):
        if hasattr(self.content, "to_notice"):
            notice_str = self.content.to_notice()
        else:
            notice_str = unicode(self.content)
        
        return notice_str

def itr_to_notices (iterable):
    return [Notice(item) for item in iterable]