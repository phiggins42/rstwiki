import cherrypy,os.path,re
from rstdocument import RstDocument
from Crumbs import Crumbs as crumbs
from auth import AuthController, require, member_of, name_is

class DocServer():
    templates = {}
     
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
    def index(self, *args): 
         return self.default(('index'))

    @cherrypy.expose
    def default(self, *args):
        basePath = self.getPath(args)
        path = self.getDocPath(basePath)
        if os.path.isfile(path):
            return open(path).read()
        elif os.path.isdir(path) and os.path.isfile(os.path.join(path,"/index.rst")):
            return self.render(self.getTemplate("master"), RstDocument(os.path.join(path,"/index.rst"),"View",basePath).render())
        elif os.path.isfile(path + ".rst"):
            return self.render(self.getTemplate("master"),RstDocument(path+".rst").render(),"View", basePath)
        else:
            if os.path.splitext(basePath)[1] != "":
                raise cherrypy.HTTPError(404)

            raise cherrypy.HTTPError(404)
            #raise cherrypy.InternalRedirect("/edit/" + basePath)
            #self.do_serv(response=200, body=open(file).read(), raw=True)                                                                            
            #return open(path).read()

    @cherrypy.expose
    def edit(self,*args,**kwargs):
        basePath = self.getPath(args)
        path = self.getDocPath(basePath)
        post=False
        if cherrypy.request.method=="POST":
            post=True

        if os.path.isfile(path):
            return open(path).read()
        elif os.path.isdir(path) and os.path.isfile(os.path.join(path,"/index.rst")):
            return self.render(self.getTemplate("editform"), RstDocument(os.path.join(path,"/index.rst"),"Edit",basePath).document)
        elif os.path.isfile(path + ".rst"):
            filename=path+".rst"
            doc=RstDocument(filename, config=self.config)
            
            if post:
                doc.update(kwargs['content'])
                doc.save()
                if self.vcs is not None:
                    print "Send Commit to VCS system"
                    self.vcs.commit(filename,message="Update Message")

                print "Internal Redirect to: %s" %(basePath)
                raise cherrypy.HTTPRedirect("/" + basePath)             
                return "Saved"
       
            body = self.fillTemplate(self.getTemplate("editform"),body=doc.document)
            return self.render(self.getTemplate("master"),body,"Edit", basePath)
        else:
            if os.path.splitext(basePath)[1] != "":
                raise cherrypy.HTTPError(404)
            raise cherrypy.HTTPError(404)

    def fillTemplate(self,template,**kwargs):
        return re.sub("{{(.*)}}", lambda m: kwargs.get(m.group(1), ""), template)

    def render(self, template, body, action, path):
        return self.fillTemplate(template,
            body = body,
            title= action + " " + path, 
            root='/_static',
            crumbs =  self.makeNavCrumbs(path),
            nav=self.editLink(path)
        )

    # FIXME get rid of this and make it part of the template
    def editLink(self, path):
        user = cherrypy.session.get("user",None)
        #print "edit LInk user: %s" %(user)
        if user is not None:
            out = "<span>[%s]</span>\n" % (user["cn"])
            #admin link to re-enable later  
            #if member_of(cherrypy.request.app.config.get("auth").get("adminGroup")):
            #    out += '<a href="/admin">admin</a>\n'

            out += "<a href='/edit/" + path + "'>edit</a>\
                    <a href='/upload/" + path + "'>upload</a>\
                    <a href='/auth/logout'>logout</a>\
                    "
            return out
        else:    
            return "<a id='loginanchor' href='/auth/login?from_page=%s'>login</a>" % (path)

    def getDocPath(self, path):
        path = os.path.join(self.config["root"],path)
        return path 

    def getPath(self, args):
        path = os.path.join(os.path.join(*args))
        return path 

    def makeNavCrumbs(self, path):
        parts = crumbs(path);
        return "<div class='crumbs'><a href='/'>home</a> / " + " / ".join(parts.links()) + "</div>"

    def getTemplate(self,name):
        if not self.templates.has_key(name):
            self.templates[name]=open(os.path.join("templates",name)+".html").read()
        return self.templates[name] 

