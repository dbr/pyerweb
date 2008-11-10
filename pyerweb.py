import re
import traceback
class Pyerweb_UrlMismatch(Exception):pass

site_functions = []

class OutputHelpers:
    def html_tidy(self, html):
        import subprocess
        tidy = subprocess.Popen(["tidy", "-i", "-c", "-q", "--tidy-mark", "n"],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        tidy.stdin.write(html)
        # print tidy.stdout.read()
        return tidy.communicate()[0]
        
class GET:
    def __init__(self, orig_url):
        self.orig_url = orig_url
        self.matcher = re.compile(orig_url)
    
    def __call__(self, func):
        def new_fun(url):
            check_url = self.matcher.match(url)
            if check_url:
                parsed_args = check_url.groups()
            else:
                raise Pyerweb_UrlMismatch(
                    "URL %s does not match %s" % (url, self.orig_url)
                )
            
            return func(*parsed_args)
        
        # Store in list of URL-mappable functions
        site_functions.append(new_fun)
        return new_fun

def pyerweb_runner(url, output_helper = None):
    try:
        for cur in site_functions:
            try:
                output_html = cur(url)
                if not (isinstance(output_html, unicode) or isinstance(output_html, str)):
                    output_html = ""
            
            except Pyerweb_UrlMismatch, errormsg:
                # The regex doesn't match, skip it
                pass
            except Exception, errormsg:
                # An actual error occured, show it
                traceback.print_exc()
            else:
                if output_helper is not None:
                    if output_helper not in dir(OutputHelpers()):
                        raise ValueError("Invalid OutputHelper %s used" % (output_helper))
                    output_html = getattr(OutputHelpers(), output_helper)(output_html)
                
                print output_html
    except Exception, errormsg:
        print """Error 500"""
        print traceback.format_exc()
# end GET

def main():
    """Example usage of GET decorator.
    An hugely imagaintive blog site example.
    Posts are hard-coded ino the self.posts dict,
    get_post returns a specified post
    """
    import textwrap
    
    TEMPLATE = """
    <html>
    <head>
    <title>%(title)s</title>
    </head>
    <body>
    %(body)s
    </body>
    </html>"""
    TEMPLATE = textwrap.dedent(TEMPLATE)
    
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
    
    @GET("^/$")
    def index():
        site = MySite()
        
        return TEMPLATE % {
            'title': "Welcome to Test Blog",
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
    
    
    # Siple dispatcher that uses fixed URLs. Will obviously be replaced by
    # a CGI script, or a simple web-server
    for request_url in ["/", "/blog/view/hello", "/admin/post/edit/hello"]:
        print "*"*15, "Request for", request_url, "*"*15
        pyerweb_runner(request_url, output_helper = "html_tidy")
        
    
if __name__ == '__main__':
    main()