import cherrypy,os.path,re
from rstdocument import RstDocument
from Crumbs import Crumbs as crumbs
from auth import AuthController, require, member_of, name_is
#from template import Template
from Cheetah.Template import Template

class DocServer():
 
    def __init__(self):
         print "Starting Wiki..."
         self.config = None
         self.vcs = None

    def start(self):
         #FIXME having to set the app myself here, need to change this
         #       it is out of the request cycle, and so cherrypy.request.config
         #       doesn't exist

         #print "Config: %s" % (cherrypy.tree.apps[''].config.keys())
         app=''
         self.config=cherrypy.tree.apps[app].config.get("wiki") 
         
         if "enable_vcs" in self.config and self.config.get("enable_vcs"):
             vcsconfig=cherrypy.tree.apps[app].config.get("vcs") 
             if vcsconfig["type"] is not None:
                 if vcsconfig['type']=="git":
                     from vcs import Git as VCS
                     self.vcs = VCS(cherrypy.tree.apps[app].config)

    @cherrypy.expose
    def index(self, *args, **kwargs): 
         if "action" in kwargs:
             print "found action on index"
             return self.default(('index'),action=kwargs['action'])
         return self.default(('index'))

    @cherrypy.expose
    def default(self, *args,**kwargs ):
        if "action" in kwargs:
           print "kwargs action: %s" % (kwargs['action'])
           action = kwargs['action'] 
        else: 
           action = None 

        basePath = self.getPath(args)
        path = self.getDocPath(basePath)
        cherrypy.request.resourceBase = basePath 
        print "action: %s" % (action) 
        if action=="edit":
            import edit
            cherrypy.request.template = template = edit.edit()
        else:
            action = "view"
            import master
            cherrypy.request.template = template = master.master()

        template.action = action
        template.path = basePath

        if os.path.isfile(path):
            return open(path).read()
        elif os.path.isdir(path) and os.path.isfile(os.path.join(path,"/index.rst")):
            template.rst =  RstDocument(os.path.join(path,"/index.rst"))
            return self.render()
        elif os.path.isfile(path + ".rst"):
            template.rst =  RstDocument(path + ".rst")
            return self.render()
        else:
            raise cherrypy.HTTPError(404)

    def render(self):
        template = cherrypy.request.template
        template.user = cherrypy.session.get("user", None)
        template.root = "/"
        template.static= "_static/"
        return template.respond()

    def getDocPath(self, path):
        path = os.path.join(self.config["root"],path)
        return path 

    def getPath(self, args):
        path = os.path.join(os.path.join(*args))
        return path 
