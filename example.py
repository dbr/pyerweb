#!/usr/bin/env python
#encoding:utf-8
"""Example usage of GET decorator.
An hugely imagaintive blog site example.
Posts are hard-coded ino the self.posts dict,
get_post returns a specified post
"""

from pyerweb import GET, runner

TEMPLATE = """<html>
<head>
<title>%(title)s</title>
</head>
<body>
%(body)s
</body>
</html>"""

class MySite:
    """Main website functionality.
    With a real site, the get/delete/edit/list posts would actually
    persist the data somewhere (a database most likely)."""
    
    def __init__(self):
        self.posts = {
            'hello':"This is a simple post",
            'another':"This is another post"
        }

    def get_post(self, postkey):
        """This would query the database for postkey"""
        return self.posts[postkey]
    
    def list_posts(self):
        ret = ""
        ret += "<ul>\n"
        for cur_post in self.posts.keys():
            ret += "<li>%s</li>\n" % (cur_post)
        ret += "</ul>"
        return ret
    
    def delete_post(self, postkey):
        del self.posts[postkey]
#end MySite

# Here are the decorated functions that map URLs to
# actions. For example, a GET request to "/" will go to
# the index function, as the regex matches "/"
# A GET request to "/blog/view/hello" will go to view_post.
# A GET request to "/a/fake/URL" will return an error 404

@GET("^/$", "/index")
def index():
    # Display the post archive by running the welcome() page
    return archive()

@GET("^/archive$")
def archive():
    site = MySite()
    
    return TEMPLATE % {
        'title': "Post archive",
        'body': site.list_posts()
    }

@GET("^/blog/view/(.+?)$")
def view_post(postkey):
    site = MySite()
    
    return TEMPLATE % {
        'title': '%s' % (postkey),
        'body': site.get_post(postkey)
    }

@GET("/admin/post/(edit|delete)/(.+?)$")
def admin_post(action, postkey):
    site = MySite()
    site.delete_post(postkey)
    return "Performing admin action %s with post %s" % (action, postkey)

@GET("^/makeanerror500$")
def makeanerror500():
    int('abc')

# Simple dispatcher that uses fixed URLs. Will obviously be replaced by
# a CGI script, or a simple web-server
for request_url in ["/",
                    "/blog/view/hello",
                    "/admin/post/edit/hello",
                    "/makeanerror404",
                    "/makeanerror500"]:
    print "*"*15, "Request for", request_url, "*"*15
    runner(request_url, output_helper = "html_tidy")
