import cherrypy
import os.path
from rstdocument import RstDocument
import re
from Crumbs import Crumbs as crumbs

class Wiki():
    templates={}
 
    def __init__(self):
         print "Starting Wiki..."

    def index(self, *args): 
         return self.default(('index'))

    index.exposed = True

    def default(self, *args):
        basePath = self.getPath(args)
        path = self.getDocPath(basePath)
        print "Looking up doc file: %s" % (path)
        if os.path.isfile(path):
            print "Found exact file: %s" %(path)
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

    default.exposed=True

    def edit(self,*args,**kwargs):
        basePath = self.getPath(args)
        path = self.getDocPath(basePath)
        post=False
        if cherrypy.request.method=="POST":
            post=True

        print "Looking up doc file: %s" % (path)
        if os.path.isfile(path):
            print "Found exact file: %s" %(path)
            return open(path).read()
        elif os.path.isdir(path) and os.path.isfile(os.path.join(path,"/index.rst")):
            return self.render(self.getTemplate("editform"), RstDocument(os.path.join(path,"/index.rst"),"Edit",basePath).document)
        elif os.path.isfile(path + ".rst"):
            doc=RstDocument(path+".rst")

            if post:
                doc.update(kwargs['content'])
                doc.save()
                print "Internal Redirect to: %s" %(basePath)
                raise cherrypy.HTTPRedirect("/" + basePath)             
                return "Saved"
       
            body = self.fillTemplate(self.getTemplate("editform"),body=doc.document)
            return self.render(self.getTemplate("master"),body,"Edit", basePath)
        else:
            if os.path.splitext(basePath)[1] != "":
                raise cherrypy.HTTPError(404)
            raise cherrypy.HTTPError(404)

    edit.exposed = True

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

    def editLink(self, path):
        return "<a href='/edit/" + path + "'>edit</a>\
                <a href='/upload/" + path + "'>upload</a>\
                "
        #else:    
        #    return "<a id='loginanchor' href='/login" + path + "'>login</a>"

    def getDocPath(self, path):
        #print "vcs.root: %s" % (cherrypy.request.config["/vcs/root"]) 
        path = os.path.join('rstwiki_git',path)
        return path 

    def getPath(self, args):
        #print "vcs.root: %s" % (vcsconf.root) 
        path = os.path.join(os.path.join(*args))
        return path 

    def makeNavCrumbs(self, path):
        #path= '/'.join(path.split("/")[1:])
        parts = crumbs(path);
        return "<div class='crumbs'><a href='/'>home</a> / " + " / ".join(parts.links()) + "</div>"

    def getTemplate(self,name):
        if not self.templates.has_key(name):
            self.templates[name]=open(os.path.join("templates",name)+".html").read()
        return self.templates[name] 

