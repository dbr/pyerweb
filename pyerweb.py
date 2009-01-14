import re
import traceback

class Pyerweb_UrlMismatch(Exception):pass
class Pyerweb_InternalServerError(Exception):pass
class Pyerweb_PageNotFound(Exception):pass

PYERWEB_SITE_FUNCTIONS = {} # Stores decorated functions

class OutputHelpers:
    def html_tidy(self, html):
        import subprocess
        tidy = subprocess.Popen(["tidy", "-i", "-c", "-q", "--tidy-mark", "n"],
            stdin = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        tidy.stdin.write(html.encode())
        return tidy.communicate()[0]

class magic_url(str):pass

class GET:
    def __init__(self, *urls):
        self.matchers = [(orig_url, matcher) for orig_url, matcher in zip(urls, list(map(re.compile, urls)))]
    
    def __call__(self, func):
        def new_fun(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], magic_url):
                # It's a Pyerweb dispatched call
                for orig_url, matcher in self.matchers:
                    check_url = matcher.match(args[0]) # request URL is first arg
                    if check_url:
                        parsed_args = check_url.groups()
                        return func(*parsed_args)
                else: # The URL did not match any of the supplied URLs
                    raise Pyerweb_UrlMismatch(
                        "URL %s does not match %s" % (args[0], orig_url)
                    )
            else:
                # It's a direct call to the function
                return func(*args, **kwargs)
        
        PYERWEB_SITE_FUNCTIONS.setdefault(self.__class__.__name__, []).append(new_fun) # Add to list of URL-mappable functions
        return new_fun

class PUT(GET):
    pass

def router(url, method = "GET"):
    if method not in PYERWEB_SITE_FUNCTIONS.keys(): raise Pyerweb_PageNotFound
    for cur in PYERWEB_SITE_FUNCTIONS[method]:
        try:
            output_html = cur(url)
            if not (isinstance(output_html, str) or isinstance(output_html, unicode)):
                output_html = ""
        except Pyerweb_UrlMismatch:
            pass # The regex doesn't match, skip it
        
        else:
            return (output_html, [("Content-type", "text/html")])
    else: # We checked all site functions, none matched, raise error 404
        raise Pyerweb_PageNotFound

def runner(environ, wsgi_start_response, url = None, method = None, output_helper = None):
    """WSGI request handler"""
    if environ is not None: # It's a WSGI call
        method = environ['REQUEST_METHOD']
        url = environ['PATH_INFO']
    else: # runner("/the/url") call
        method = "GET" if method is None else method
        url = magic_url(url) # Wrap URL string into magic_url class
    # If the call to @GET decorator __call__() is a magic_url then
    # then the request came from here, if not it's a direct call!
    
    output_headers = [("Content-type", "text/html")] # Default header
    try:
        output_html, output_headers = router(url, method = method)
    except Pyerweb_PageNotFound:
        output_response = '404 Not Found'
        output_html = "<html><head><title>ERROR 404</title></head><body>The URL %s could not be found</body></html>" % (url)
    except Exception: # unhandled error!
        output_response = '500 Internal Server Error'
        tb = traceback.format_exc()
        output_html = "<html><head><title>ERROR 500</title></head><body><p>Internal server error! The following error occured:</p><pre>%s</pre></body></html>" % (tb)
    print "I GOT OUTPUT!"
    print output_html
    print output_headers
    # if output_helper is not None:
    #     if output_helper not in dir(OutputHelpers()):
    #         raise ValueError("Invalid OutputHelper %s used" % (output_helper))
    #     output_html = getattr(OutputHelpers(), output_helper)(output_html)

    if output_html is None:
        output_response = "204 No Content"
    wsgi_start_response("200 OK", output_headers)
    return output_html
