import cherrypy,os.path,re,urlparse
from rstdocument import RstDocument
from Crumbs import Crumbs as crumbs
from auth import AuthController, require, member_of, name_is
from Cheetah.Template import Template
from pprint import pprint
import mimetypes

class Github(cherrypy.Application):
    def __init__(self, script_name="", config=None):
        cherrypy.Application.__init__(self, GithubServer(), script_name, config)

class GithubServer():
 
    def __init__(self):
         print "Starting Github..."

    @cherrypy.expose
    def index(self, *args, **kwargs): 
        return "<h2>Arg matey, eye be a workn</h2>"

    @cherrypy.expose
    def postcommit(self,*args,**kwargs):
        pprint(args)
        pprint(kwargs)
        return "<pre>%s</pre><hr><pre>%s</pre>" %(pprint(args),pprint(kwargs))
