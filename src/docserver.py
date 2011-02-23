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
         '''
                FIXME having to set the app myself here, need to change this
                it is out of the request cycle, and so cherrypy.request.config
                doesn't exist
         '''

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
        '''
            Main index file, just goes to default
        '''
        return self.default(*args,**kwargs)

    @cherrypy.expose
    def default(self, *args, **kwargs):
        '''
            This is the main handler for any requests
            recieved on this mount point.
        '''

        if cherrypy.request.method != "GET" and cherrypy.session.get("user",None) is None:
            raise cherrypy.HTTPError(401, "Not authorized to %s to this source" %(cherrypy.request.method))


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
        '''
           When the self.default() detects a POST, it sends it here for processing.
           This method returns an action so default () can decide how to proceed
        '''
         
        #if this form post has 'content' and we're writing to a .rst 
        if 'content' in kwargs and cherrypy.request.resourceFileExt == ".rst":
            message = kwargs['message'] or "Updates to %s%s via Wiki" % (cherrypy.request.resourceDir,cherrypy.request.resourceFile)
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
                 # there was an error, send them back to the edit form
                 # the edit form template can make use of cherrypy.request.formPostError if desired
                 cherrypy.request.formPostError = err
 
                 return "edit"

        print "POST to dir: %s " % (cherrypy.request.resourceDir)

        #handle file uploads
        for key in kwargs.keys():
            if key.startswith("uploadfile"):
                print "key: %s" % (key)
                if kwargs[key].filename:
                    print "Handle upload of %s (%s)" %(kwargs[key].filename,kwargs[key].file)
                    filename = os.path.join(self.config["root"], cherrypy.request.resourceDir,kwargs[key].filename)
                    isNew = os.path.isfile(filename)

                    outfile = open(os.path.join(filename),'wb')
                    while True:
                        data = kwargs[key].file.read(8192)
                        if not data:
                            break
                        outfile.write(data)
                    outfile.close()
                    if self.vcs is not None:
                        if isNew:
                            message = "*** ADDED *** new file '%s' to %s" % (kwargs[key].filename, cherrypy.request.resourceDir)
                        else:
                            message = "Updated '%s' to %s" % (kwargs[key].filename, cherrypy.request.resourceDir)

                        print "Send Commit to VCS system"
                        print "   Message: %s" % (message) 
                        self.vcs.add(filename) 
                        self.vcs.commit(filename,message=message)


        return "view"

    def render(self):
        '''
            Setup some template vars we want to be available on all
            requests. Then tell the template to render (respond()) 
        '''
        template = cherrypy.request.template
        template.resourceDir = cherrypy.request.resourceDir
        template.resourceFile = cherrypy.request.resourceFile
        template.user = cherrypy.session.get("user", None)
        template.root = "/"
        template.static= "_static/"
        return template.respond()

    def parsePath(self, args):
        root = self.config["root"]

        for arg in args:
            if arg[0]==".": 
                raise cherrypy.HTTPError(404)

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



