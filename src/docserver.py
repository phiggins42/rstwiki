import cherrypy,os.path,re,urlparse,cgi
from rstdocument import RstDocument
from Crumbs import Crumbs as crumbs
from auth import AuthController, require, member_of, name_is
from Cheetah.Template import Template
from pprint import pprint
import mimetypes, urllib

class Wiki(cherrypy.Application):
    def __init__(self, script_name="", config=None):
        docserver = DocServer() 
        cherrypy.Application.__init__(self, docserver, script_name, config)
        docserver.initVCS(self)

class DocServer():
 
    def __init__(self):
        print "Starting Wiki..."
        self._triggerurl = None

    def initVCS(self,app):
        wiki = app.config.get('wiki')
        if "enable_vcs" in wiki and wiki.get("enable_vcs"):
            vcsconfig = app.config.get("vcs") 
            if vcsconfig["type"] is not None:
                if vcsconfig['type'] == "git":
                    from vcs import Git as VCS
                    app.vcs = VCS(app.config)
                    if vcsconfig["postrecieve"] is not None:
                        self._triggerurl = vcsconfig["postrecieve"]
                     
        self.githubroot = wiki.get("githubroot", None)
        
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

        usar = cherrypy.session.get("user", None)
        if usar is not None:
            print usar.keys()

        if cherrypy.request.method != "GET" and usar is None:
            # if we've setup a post-recieve hook, check out this first.
            if self._triggerurl == cherrypy.request.path_info and cherrypy.request.app.vcs is not None:
                # perhaps do some exception handling and put a warning on .app that merge conflict happened?
                cherrypy.request.app.vcs.pull()
                return ""
            else:
            # otherwise:
                raise cherrypy.HTTPError(401, "Not authorized to %s to this source" %(cherrypy.request.method))

        if "action" in kwargs:
           action = kwargs['action'] 
        else: 
           action = "view"

        self.parsePath(args)

        if cherrypy.request.method == "POST":
           action=self._handlePost(args,**kwargs)

        if action == "create" and usar is not None and cherrypy.request.resourceFileExt == ".rst":
            
            import create
            cherrypy.request.template = template = create.create()
            print "Showing create page %s" % (cherrypy.request.path_info)
            
            filename = cherrypy.request.path_info[1:]
            title = filename.replace("/", ".")
            heading = "=" * len(title)
            
            somerst = ".. _%s:\n\n%s\n%s\n\nTODOC!\n\n.. contents ::\n  :depth: 2\n\n=============\nFirst Section\n=============\n\n" % (filename, title, heading)
            
            template.rst = RstDocument();
            template.rst.update(somerst);
            template.encoded_rst = cgi.escape(template.rst.document)
            template.title = "Creating: %s" % (template.rst.gettitle())
            template.action = action
            cherrypy.response.status = 404;
            return self.render()
            
        elif action == "edit":
            import edit
            cherrypy.request.template = template = edit.edit()
        elif action == "upload":
            import upload
            cherrypy.request.template = template = upload.upload()
        elif action == "bare":
            if 'id_prefix' in kwargs:
                print "id_prefix: "+ kwargs["id_prefix"]
                return cherrypy.request.rst.render(settings_overrides={'id_prefix': kwargs['id_prefix']})
            return cherrypy.request.rst.render()            
        else:
            action = "view"
            import master
            cherrypy.request.template = template = master.master()
            cherrypy.request.githublink = self.githubroot

        template.action = action

        if cherrypy.request.resourceFileExt != ".rst":
            mimetype = mimetypes.guess_type(cherrypy.request.resourceFilePath) 
            cherrypy.response.headers["Content-Type"] = mimetype[0]
            return open(cherrypy.request.resourceFilePath).read()
        elif os.path.isfile(cherrypy.request.resourceFilePath):
            template.rst =  RstDocument(cherrypy.request.resourceFilePath)
            template.encoded_rst = cgi.escape(template.rst.document)
            template.title = template.rst.gettitle()
        else:

            get_parmas = urllib.quote(cherrypy.request.request_line.split()[1])
            creating = get_parmas.find("?action=create")
            
            if creating >= 0:
                raise cherrypy.HTTPError(404);
            else:
                redir = get_parmas + "?action=create"    
                raise cherrypy.HTTPRedirect(redir)
            
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

                # this ensures the document will be created if not already existing
                doc = cherrypy.request.rst = RstDocument()
                doc.path = cherrypy.request.resourceFilePath;
                doc.update(kwargs['content'].replace("\r", ""))
                doc.save()
                
                try:
                    if cherrypy.request.app.vcs is not None:
                        print "Send Commit to VCS system"
                        print "   Message: %s" % (message) 
                        cherrypy.request.app.vcs.commit(cherrypy.request.resourceFilePath,message=message)
                except Exception,err:
                    print "Error committing to VCS: %s" % err

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

                    print "Handle upload of %s (%s) to %s" % (
                        kwargs[key].filename,
                        kwargs[key].file,
                        cherrypy.request.resourceFilePath 
                    )
                    
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
                                message = "*** ADDED *** new file '%s' to %s" % (
                                    kwargs[key].filename, 
                                    cherrypy.request.path_info
                                )
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
        # FIXME: this should be from a per-mount conf, no?
        template.static = "/_static/"
        template.editable = cherrypy.request.app.config.get("wiki")["editable"]
         
        return template.respond()

    def parsePath(self, args):
        root = cherrypy.request.app.config.get('wiki').get('root')
        path_info = cherrypy.request.path_info
        parts = path_info.split("/")

        for p in parts:
            if len(p) > 0 and p[0] == ".":
                raise cherrypy.HTTPError(401)

        plen = len(parts)
        if os.path.isfile(root + path_info):
            cherrypy.request.resourceFilePath=root+path_info
            cherrypy.request.relativeResourcePath = path_info
        elif plen > 0 and parts[plen - 1] == '': 
            fn = os.path.join(os.path.join(root, *parts[0:-1]), "index.rst")
            cherrypy.request.resourceFilePath = fn
            cherrypy.request.relativeResourcePath = os.path.join(*parts[0:-1]) + "/index.rst"
        else:
            fp = cherrypy.request.resourceFilePath = root + path_info + ".rst"
            cherrypy.request.relativeResourcePath = path_info + ".rst"
            if not os.path.isfile(cherrypy.request.resourceFilePath):
                if os.path.isdir(root + path_info):
                     cherrypy.request.resourceFilePath= root + path_info + "/index.rst"
                     cherrypy.request.relativeResourcePath = path_info + "/index.rst"
                     
        cherrypy.request.resourceFileExt = os.path.splitext(cherrypy.request.resourceFilePath)[1]
        # print "FILE: %s EXT: %s" % (cherrypy.request.resourceFilePath, cherrypy.request.resourceFileExt)
