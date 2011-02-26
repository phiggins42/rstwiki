import cherrypy,os,re
from dojo import DojoHTMLWriter
from docutils import core, io
import inspect
from docutils.parsers.rst.roles import register_canonical_role
from docutils.nodes import literal_block, TextElement, FixedTextElement, Element, General
from docutils import nodes, utils, statemachine
from directives import *

class RstDocument():
    def __init__(self,path=None,**kwargs):
        if path is not None:
            self.path = path
            self.document=open(path).read()
        else:
            self.path = None
            self.document=None 

    def render(self,*args,**kwargs):
        return self.parse_data(self.path, self.document)
 
    def parse_data(self, path, out):
        return core.publish_parts(
            source=self.document, source_path="/",
            destination_path="/", writer=DojoHTMLWriter(), settings_overrides={'id_prefix':cherrypy.request.script_name + "/"})['html_body']

    def create(self, *args, **kwargs):
        return "Create"

    def update(self, content):
        self.document = content

    def save(self):
        dir = os.path.dirname(self.path)
        if not os.path.exists(dir):
            os.makedirs(dir)
               
        if not os.path.exists(self.path): 
            isNewFile=True
        open(self.path, 'w').write(self.document)
        print "Saving Document."

# define a `ref:` role for reST, need to override the one in dojo.py to make sure we are relative to request.script_name
def ref_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    # match :ref:`Bar! <link/link/link>` from rawText
    p = re.search('`(.*) <(.*)>`', rawtext)
    if(p):
        return [nodes.reference(rawtext, p.group(1), refuri= cherrypy.request.script_name + "/" + p.group(2), **options)], []   
    else:
        return [], []
    # also, this could be safer:

register_canonical_role("ref", ref_role)
