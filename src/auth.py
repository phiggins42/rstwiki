#here lies a bunch of auth tools, somewhat modified, taken from the cherrypy wiki
#will probably change to a more plugged/standardized system in the future

import cherrypy,urllib


SESSION_KEY = '_cp_username'

def check_credentials(username, password):
    """
        Verifies credentials for username and password.
        Returns None on success or a string describing the error on failure
    """

    
    authconf = cherrypy.request.app.config.get("auth")
    authtype = authconf.get('type',None)

    if authtype=='ldap':
        from ldapauth import isuser
        if isuser(username, password):
           return None
        else:
           return u"Incorrect username or password."

    #untested, but should bypass auth if you set it in your config.  You should still login.
    if authtype=="bypass":
        cherrypy.session["user"] = { 'uname': username, 'groups': [] }
        return None
    
def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as alist of
    conditions that the user must fulfill"""

    conditions = cherrypy.request.config.get('auth.require', None)
     
    # format GET params
    get_parmas = urllib.quote(cherrypy.request.request_line.split()[1])
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username

            for condition in conditions:
                # A condition is just a callable that returns true orfalse
                if not condition():
                    # Send old page as from_page parameter
                    raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" % get_parmas)
        else:
            # Send old page as from_page parameter
            raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" %get_parmas) 
    else:
         username = cherrypy.session.get(SESSION_KEY)
         if username:
            cherrypy.request.is_authenticated = True
         else:
            cherrypy.request.is_authenticated = False

   

cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        authconf = cherrypy.request.app.config.get("auth") 
        authtype = authconf.get("type")
        if type=="ldap":
            User = cherrypy.session.get("User",None)
            if User is not None: 
                if groupname in User.get("groups"):
                    return True
        
            return False

        return cherrypy.request.login == 'joe' and groupname == 'admin'
    return check

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy

def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


# Controller to provide login and logout actions

class AuthController(object):
    
    def on_login(self, username):
        """Called on successful login"""
    
    def on_logout(self, username):
        """Called on logout"""
    
    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        import login
        #from login import login as loginTemplate
         
        template = login.login()
        template.resourceDir= "auth/login"
        template.resourceFile=""
        template.static = "/_static/"
        template.root = "/"
        template.action="Login"
        template.from_page = from_page
        return template.respond() 

    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)
        
        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect("/" + from_page or "/")
    
    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        sess["user"]=None

        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")

