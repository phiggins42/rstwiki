import cherrypy,os.path,re,urlparse
from rstdocument import RstDocument
from Crumbs import Crumbs as crumbs
from auth import AuthController, require, member_of, name_is
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
        return self.default(*args,**kwargs)

    @cherrypy.expose
    def default(self, *args, **kwargs):
        if "action" in kwargs:
           action = kwargs['action'] 
        else: 
           action = "view"

        self.parsePath(args)

        if cherrypy.request.method == "POST":
           action=self._handlePost(args,**kwargs)

        if action=="edit":
            import edit
            cherrypy.request.template = template = edit.edit()
        elif action=="upload":
            import upload
            cherrypy.request.template = template = upload.upload()
        else:
            action = "view"
            import master
            cherrypy.request.template = template = master.master()

        template.action = action

        if cherrypy.request.resourceFileExt != ".rst":
            return open(cherrypy.request.resourceFilePath).read()
        elif os.path.isfile(cherrypy.request.resourceFilePath):
            template.rst =  RstDocument(cherrypy.request.resourceFilePath)
        else:
            raise cherrypy.HTTPError(404)
 
        return self.render()

    def _handlePost(self, *args, **kwargs):
        print "DO POST %s" % (cherrypy.request.resourceFileExt)
        if cherrypy.request.resourceFileExt == ".rst":
            message = kwargs['message'] or "Documentation Update of %s%s via Wiki" % (cherrypy.request.resourceDir,cherrypy.request.resourceFile)

            try:
                doc=RstDocument(cherrypy.request.resourceFilePath, config=self.config)
                doc.update(kwargs['content'])
                doc.save()
                if self.vcs is not None:
                    print "Send Commit to VCS system"
                    print "   Message: %s" % (message) 
                    self.vcs.commit(cherrypy.request.resourceFilePath,message=message)

                return "view"
            
            except Exception,err:
                 print "Error updating file %s" %(err)
                 cherrypy.request.formPostError = err
                 return "edit"

        print "POST to dir: %s " % (cherrypy.request.resourceDir)

        #handle file uploads
        for key in kwargs.keys():
            if key.startswith("uploadfile"):
                print "key: %s" % (key)
                if kwargs[key].filename:
                    print "Handle upload of %s (%s)" %(kwargs[key].filename,kwargs[key].file)
                    outfile = open(os.path.join(self.config["root"], cherrypy.request.resourceDir,kwargs[key].filename),'wb')
                    while True:
                        data = kwargs[key].file.read(8192)
                        if not data:
                            break
                        outfile.write(data)
                    outfile.close()

        return "view"

    def render(self):
        template = cherrypy.request.template
        template.resourceDir = cherrypy.request.resourceDir
        template.resourceFile = cherrypy.request.resourceFile
        template.user = cherrypy.session.get("user", None)
        template.root = "/"
        template.static= "_static/"
        return template.respond()

    def getDocPath(self, path):
        path = os.path.join(self.config["root"],path)
        return path 

    def getPath(self, args):
        if len(args)<0:
            return "index"
        return os.path.join(os.path.join(*args))

    def parsePath(self, args):
        root = self.config["root"]
        if len(args)<1:
            cherrypy.request.resourceDir = ""
            cherrypy.request.resourceFile = "index"
            cherrypy.request.resourceFilePath = os.path.join(root,"index.rst")
        else:
            pinfo =  cherrypy.request.wsgi_environ["PATH_INFO"]  
            requestForDir = False
            if pinfo[len(pinfo)-1]=='/':
                requestForDir = True

            #print "requestForDir%s", requestForDir
            #print "First Check %s %s " % ( requestForDir is False,  os.path.isdir(os.path.join(root, os.path.join(*args))+".rst"))
            
            if requestForDir is False and os.path.isfile(os.path.join(root, os.path.join(*args))+".rst"):
                cherrypy.request.resourceDir = str(os.path.join(*args[0:-1])) + "/"
                cherrypy.request.resourceFile=args[-1]   
                cherrypy.request.resourceFilePath = os.path.join(root,os.path.join(*args)) + ".rst"
            elif os.path.isdir(os.path.join(root, os.path.join(*args))):
                cherrypy.request.resourceDir = os.path.join(*args) + "/"
                cherrypy.request.resourceFile = "index"
                cherrypy.request.resourceFilePath = os.path.join(root,os.path.join(*args),"index")+".rst"

            elif os.path.isfile(os.path.join(root,os.path.join(*args))):
                cherrypy.request.resourceDir = str(os.path.join(args[0:-1])) + "/"
                cherrypy.request.resourceFile = args[-1]   
                cherrypy.request.resourceFilePath = os.path.join(root,os.path.join(*args))
           
            else:
                cherrypy.request.resourceDir = str(os.path.join(args[0:-1])) + "/"
                cherrypy.request.resourceFile=args[-1]   
                cherrypy.request.resourceFilePath = os.path.join(root,os.path.join(*args)) + ".rst"

        p = os.path.splitext(cherrypy.request.resourceFilePath)
        cherrypy.request.resourceFileExt = p[1] 
        print "DIR: %s FILE: %s FILEPATH: %s EXT: %s" % (cherrypy.request.resourceDir,cherrypy.request.resourceFile, cherrypy.request.resourceFilePath, cherrypy.request.resourceFileExt) 
