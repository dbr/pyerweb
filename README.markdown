pyerweb: an absurdly small Python web-framework

Currently pyerweb is basically a simple routing system, which allows you to do the following:

    import wsgiref.handlers
    from pyerweb import GET, runner

    @GET("^/view/(.+?)")
    def view(key):
        return "Viewing %s" % (key)

    if __name__ == "__main__":
        wsgiref.handlers.CGIHandler().run(runner)

You simply decorate a function with `@GET`, `@PUT` `@POST` or `@DELETE`, the argument is a regular expression (in a string), for example:

    @POST("^/0-9+$")

..will match a POST request to `/1` or `/44532`

Groups in the regular expression will be passed to the decorated function as arguments, for example:

    @POST("^/(0-9)+$")
    def view(the_number):
        pass

..will grab the supplied number as `the_number` argument

The `runner` function is the WSGI compatible runner. For example, using "spawning" you can simply run:

    spawn myscript.runner