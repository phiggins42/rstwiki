import cherrypy,os
from dojo import DojoHTMLWriter
from docutils import core, io
import inspect

class RstDocument():
    def __init__(self,path):
        print "Opening %s" % (path) 
        self.path = path
        self.document=open(path).read()

    def render(self,*args,**kwargs):

        return self.parse_data(self.path, self.document)
 
    def parse_data(self, path, out):
        return core.publish_parts(
            source=self.document, source_path="/",
            destination_path="/", writer=DojoHTMLWriter(), settings_overrides={})['html_body']

    def create(self, *args, **kwargs):
        return "Create"

    def update(self, content):
        self.document = content
        print "Updated Content for %s." % (self.path)

    def save(self):
        dir = os.path.dirname(self.path)
        if not os.path.exists(dir):
            os.makedirs(dir)
               
        if not os.path.exists(self.path): 
            isNewFile=True
        open(self.path, 'w').write(self.document)
        print "Saving Document."

