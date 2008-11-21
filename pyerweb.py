import re
import traceback

class Pyerweb_UrlMismatch(Exception):pass
class Pyerweb_InternalServerError(Exception):pass
class Pyerweb_PageNotFound(Exception):pass

PYERWEB_SITE_FUNCTIONS = [] # Stores decorated functions

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

class magic_url(str):pass

class GET:
    def __init__(self, orig_url):
        self.orig_url = orig_url
        self.matcher = re.compile(orig_url)
    
    def __call__(self, func):
        def new_fun(*args, **kwargs):
            if isinstance(args[0], magic_url):
                # It's a Pyerweb dispatched call
                check_url = self.matcher.match(args[0]) # request URL is first arg
                if check_url:
                    parsed_args = check_url.groups()
                else:
                    raise Pyerweb_UrlMismatch(
                        "URL %s does not match %s" % (url, self.orig_url)
                    )
                return func(*parsed_args)
            else:
                # It's a direct call to the function
                return func(*args, **kwargs)
        
        PYERWEB_SITE_FUNCTIONS.append(new_fun) # Add to list of URL-mappable functions
        return new_fun

def router(url):
    for cur in PYERWEB_SITE_FUNCTIONS:
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
            return output_html
    else: # We checked all site functions, none matched, raise error 404
        raise Pyerweb_PageNotFound

def runner(url, output_helper = None):
    url = magic_url(url) # Wrap URL string into magic_url class
    # If the call to @GET decorator __call__() is a magic_url then
    # then the request came from here, if not it's a direct call!
    
    try:
        output_html = router(url)
    except Pyerweb_PageNotFound, errormsg:
        output_html = "<html><head><title>ERROR 404</title></head><body>The URL %s could not be found</body></html>" % (url)
    except Pyerweb_InternalServerError, errormsg:
        output_html = "<html><head><title>ERROR 500</title></head><body><p>Internal server error! The following error occured:</p><pre>%s</pre></body></html>" % (errormsg)
        
    
    if output_helper is not None:
        if output_helper not in dir(OutputHelpers()):
            raise ValueError("Invalid OutputHelper %s used" % (output_helper))
        output_html = getattr(OutputHelpers(), output_helper)(output_html)
    
    print output_html
