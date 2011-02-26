import cherrypy,os.path,re,urlparse
from rstdocument import RstDocument
from Crumbs import Crumbs as crumbs
from auth import AuthController, require, member_of, name_is
from Cheetah.Template import Template
from pprint import pprint
import mimetypes

class Wiki(cherrypy.Application):
    def __init__(self, script_name="", config=None):
        docserver = DocServer() 
        cherrypy.Application.__init__(self, docserver, script_name, config)
        docserver.initVCS(self)

class DocServer():
 
    def __init__(self):
         print "Starting Wiki..."

    def initVCS(self,app):
         wiki = app.config.get('wiki')
         if "enable_vcs" in wiki and wiki.get("enable_vcs"):
             vcsconfig=app.config.get("vcs") 
             if vcsconfig["type"] is not None:
                 if vcsconfig['type']=="git":
                     from vcs import Git as VCS
                     app.vcs = VCS(app.config)

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
        elif action=="bare":
            return cherrypy.request.rst.render()            
        else:
            action = "view"
            import master
            cherrypy.request.template = template = master.master()

        template.action = action

        if cherrypy.request.resourceFileExt != ".rst":
            mimetype = mimetypes.guess_type(cherrypy.request.resourceFilePath) 
            cherrypy.response.headers["Content-Type"] = mimetype[0]
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
	
        
	if 'preview' in kwargs:
            cherrypy.request.rst = RstDocument()
            cherrypy.request.rst.document=kwargs['preview']
            return "bare"	
            
 
        #if this form post has 'content' and we're writing to a .rst 
        if 'content' in kwargs and cherrypy.request.resourceFileExt == ".rst":
            message = kwargs['message'] or "Updates to %s via Wiki" % (cherrypy.request.path_info)
            try:
                doc = cherrypy.request.rst = RstDocument(cherrypy.request.resourceFilePath)
                doc.update(kwargs['content'])
                doc.save()
                if cherrypy.request.app.vcs is not None:
                    print "Send Commit to VCS system"
                    print "   Message: %s" % (message) 
                    cherrypy.request.app.vcs.commit(cherrypy.request.resourceFilePath,message=message)

                return kwargs['action'] or 'view'
            
            except Exception,err:
                 print "Error updating file %s" %(err)
                 # there was an error, send them back to the edit form
                 # the edit form template can make use of cherrypy.request.formPostError if desired
                 cherrypy.request.formPostError = err
                 if kwargs['action']=='bare':
                    raise cherrypy.HTTPError(500,err)
                      
                 return "edit"

        #handle file uploads
        for key in kwargs.keys():
            if key.startswith("uploadfile"):
                print "key: %s" % (key)
                if kwargs[key].filename:
                    print "Handle upload of %s (%s) to %s" %(kwargs[key].filename,kwargs[key].file,cherrypy.request.resourceFilePath )
                    parts = os.path.split(cherrypy.request.resourceFilePath)
                    if os.path.isdir(parts[0]):
                        filename = os.path.join(parts[0],kwargs[key].filename)
                        isNew = os.path.isfile(filename)

                        outfile = open(os.path.join(filename),'wb')
                        while True:
                            data = kwargs[key].file.read(8192)
                            if not data:
                                break
                            outfile.write(data)
                        outfile.close()
                        if cherrypy.request.app.vcs is not None:
                            if isNew:
                                message = "*** ADDED *** new file '%s' to %s" % (kwargs[key].filename, cherrypy.request.path_info)
                            else:
                                message = "Updated '%s' to %s" % (kwargs[key].filename, cherrypy.request.path_info)

                            print "Send Commit to VCS system"
                            print "   Message: %s" % (message) 
                            cherrypy.request.app.vcs.add(filename) 
                            cherrypy.request.app.vcs.commit(filename,message=message)


        return "view"

    def render(self):
        '''
            Setup some template vars we want to be available on all
            requests. Then tell the template to render (respond()) 
        '''
        template = cherrypy.request.template
        template.user = cherrypy.session.get("user", None)
        template.static= "/_static/"
        template.editable = cherrypy.request.app.config.get("wiki")["editable"]
         
        return template.respond()

    def parsePath(self, args):
        root=cherrypy.request.app.config.get('wiki').get('root')
        path_info = cherrypy.request.path_info
        parts = path_info.split("/")
        pprint(parts)
        for p in parts:
            if len(p)>0 and p[0]==".":
                raise cherrypy.HTTPError(401)

        plen = len(parts)
        if os.path.isfile(root + path_info):
            cherrypy.request.resourceFilePath=root+path_info
        elif plen>0 and parts[plen-1]=='': 
            fn = os.path.join(os.path.join(root,*parts[0:-1]),"index.rst")
            cherrypy.request.resourceFilePath=fn
        else:
            fp = cherrypy.request.resourceFilePath= root + path_info + ".rst"
            if not os.path.isfile(cherrypy.request.resourceFilePath):
                if os.path.isdir(root + path_info):
                     cherrypy.request.resourceFilePath= root + path_info + "/index.rst"
            
         
        cherrypy.request.resourceFileExt = os.path.splitext(cherrypy.request.resourceFilePath)[1]
        print "FILE: %s EXT: %s" % (cherrypy.request.resourceFilePath, cherrypy.request.resourceFileExt)



