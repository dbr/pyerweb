"""Templating thing-y in Python, along the lines of cl-who or HAML"""

from __future__ import with_statement

import sys
from StringIO import StringIO

class TagObject:
    def __init__(self, name, params = None):
        """Requires a tag name. Optionally takes attributes as a dict
        
        TagObject("html")
        
        TagObject("div", params = {"id": "mydiv"})
        """
        self.name = name
        self.params = params
        
        self.response = StringIO()

    def _openTag(self, autoclose = False):
        if self.params is not None:
            return "<%s %s%s>" % (
                self.name,
                " ".join(["%s=\"%s\"" % (k, v)for k, v in self.params.items()]),
                ' /' * autoclose
            )
        else:
            return "<%s>" % (self.name)

    def __repr__(self):
        """Used for single self-closing tag:
        t = TagGen()
        print t.img(src="http://example.com/photo.png")
        """
        return self._openTag(autoclose = True)

    def __call__(self, *args, **kwargs):
        """Used for tags with attributes:
        t = TagGen()
        with t.div(id = "test"):
            pass
        """
        return TagObject(name = self.name, params = kwargs)
    
    def __enter__(self):
        """Used for with statement. Captures stdout to self.response, then
        prints opening tag"""
        self.orig_stdout = sys.stdout
        sys.stdout = self.response
        
        print self._openTag()
    
    def __exit__(self, a, b, c):
        """Used for with statement. Prints closing tag, then displays all
        output since start of with statement. Also restores stdout"""
        print "</%s>" % self.name,
        self.response.seek(0)
        contents = self.response.read()
        sys.stdout = self.orig_stdout
        print contents

class TagGen:
    """Generates TagObject's in a nicer to use way:
    t = TagGen()
    with t.html:
        pass
    
    is equivalent to:
    
    with TagObject("html"):
        pass
    """
    def __getattr__(self, key):
        return TagObject(name = key)

if __name__ == '__main__':
    t = TagGen()
    
    print """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">"""
    with t.html:
        with t.head:
            with t.title:
                print "Hi"
        with t.h1(style="background-color:#000;color:#fff"):
            print t.img(src="http://www.google.co.uk/intl/en_uk/images/logo.gif")
