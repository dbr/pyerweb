import re
import traceback

class Pyerweb_UrlMismatch(Exception):pass
class Pyerweb_InternalServerError(Exception):pass
class Pyerweb_PageNotFound(Exception):pass

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

def router(url):
    url_match = False
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
            tb = traceback.format_exc()
            raise Pyerweb_InternalServerError(tb)
        
        else:
            url_match = True
            return output_html
    else:
        if not url_match:
            raise Pyerweb_PageNotFound

def runner(url, output_helper = None):
    try:
        output_html = router(url)
    except Pyerweb_PageNotFound:
        output_html = "<html><head><title>ERROR 404</title></head><body>The URL %s could not be found</body></html>" % (url)
    
    if output_helper is not None:
        if output_helper not in dir(OutputHelpers()):
            raise ValueError("Invalid OutputHelper %s used" % (output_helper))
        output_html = getattr(OutputHelpers(), output_helper)(output_html)
    
    print output_html
