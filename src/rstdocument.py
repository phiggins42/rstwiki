import cherrypy,os,re
from dojo import DojoHTMLWriter
from docutils import core, io
import inspect, codecs
from docutils.parsers.rst.roles import register_canonical_role
from docutils.nodes import literal_block, TextElement, FixedTextElement, Element, General
from docutils import nodes, utils, statemachine
from directives import *

class RstDocument():
    def __init__(self,path=None,**kwargs):
        
        if path is not None:
            self.path = path
            self.document = codecs.open(path, "r", encoding="utf8").read()
        else:
            self.path = None
            self.document = None 


    def render(self,*args,**kwargs):
        return self.parse_data(self.path, self.document,**kwargs)
 
    def parse_data(self, path, out,**kwargs):
        if "settings_overrides" in kwargs:
            over = kwargs['settings_overrides']
        else:
            over = None 

        self._content = core.publish_parts(
            source=self.document, source_path="/",
            destination_path="/", writer=DojoHTMLWriter(), settings_overrides=over)
                        
        return self._content['html_body']

    def gettitle(self):
        self.render()
        return self._content['title']

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

        print "Saving %s" % self.path
        f = codecs.open(self.path, "w", encoding="utf8");    
        f.write(self.document)
        f.close();


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
