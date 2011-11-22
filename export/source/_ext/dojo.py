"""
    Dojo specific rst/sphinx directives
"""

import types, re, json, cgi

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

from docutils import nodes, utils, statemachine
from docutils.nodes import literal_block, TextElement, FixedTextElement, Element, General
from docutils.parsers import rst
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.roles import register_canonical_role
from docutils.writers.html4css1 import HTMLTranslator, Writer

import urllib

class LiveCode(Directive):
    
    required_arguments = 0
    optional_arguments = 3
    has_content = True
    
    def run(self):
        raw = u"\n".join(self.content)

        try:
            # it's always html.
            lexer = get_lexer_by_name("html")
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()

        formatter = HtmlFormatter(noclasses=False, style='fruity')
        formatted = highlight(raw, lexer, formatter)

        markup = """
            <div class='live-example'>
                <div class='inner'>%s</div>
                <div class='closed'>
                    <p>Example Source:</p>
                    %s
                </div>
            </div>
            """ % ( raw, formatted )
            
        return [nodes.raw('', markup, format='html')]
        

class DojoApi(Directive):
    """ Dojo API Documentation inlining
    """
    required_arguments = 1
    optional_arguments = 0
    has_content = False
    
    def run(self):
        
        api = self.arguments[0];
        apislashed = api.replace(".", "/")
        apidotted = api.replace("/", ".")
        
        # insert code here to generate some markup for `api` ... ttrenka might already have these cached
        # as part of the api doc generation.
        markup = "<p class='apiref'>API Rerence: <a target='_api' href='http://dojotoolkit.org/api/%s'>%s</a></p>" % ( apislashed, apidotted )
            
        return [nodes.raw('', markup, format='html')]


dojo_api_inline_cache = {}

class DojoApiInline(Directive):
    """ Put a root API block in this place in RST format. Tie into the parser stream and dump this back for processing.

        TODO: change this API. 

        Currently it's omission based. eg:
            .. api-inline :: foo.bar # shows Everything
            .. api-inline :: foo.bar # shows Everything but examples
                :no-examples:

        This should be rejiggered to be inclusive, except "Evertyhing" eg:
            .. api-inline :: foo.bar # shows Everything
            .. api-inline :: foo.bar # shows only Examples--- and Signature--- subheadings
                :examples:
                :signature:

        # with one global ommission rule, :no-titles:
            .. api-inline :: foo.bar # shows only signature text, no headings or TOC entries for signature inline
                :no-titles:
                :signature:

        Also should maybe allow configurable heading depth? eg using =, -, ~ as heading markers?
    """
    
    required_arguments = 1
    optional_arguments = 10
    has_content = False

    base_url = "http://dojotoolkit.org/api/rpc/" # json api
    #base_url = "http://staging.dojotoolkit.org/api/lib/html.php?p=" # raw html dumper. 

    def run(self):

        arguments = self.arguments
        
        if len(arguments) == 1:
            includelink = showmethods = showproperties = showexamples = showtitles = showsummary = showsignature = showlongsignature = showreturns = True
        else:
            showexamples = ":examples:" in arguments
            showtitles = ":no-titles:" not in arguments
            showsummary = ":summary:" in arguments
            showsignature = ":signature:" in arguments
            showlongsignature = ":longsignature:" in arguments
            showreturns = ":returns:" in arguments
            showmethods = ":methods:" in arguments
            showproperties = ":properties:" in arguments
            includelink = ":includelink:" in arguments
            
        api = self.arguments[0];
        apislashed = api.replace(".", "/")
        apidotted = api.replace("/", ".")
        
        target_url = self.base_url + apislashed

        try:
            
            if not target_url in dojo_api_inline_cache:
                # maybe add a local caching mechaism here too. eg, save the read() stream to a local fs
                print "not found. caching", target_url
                data = urllib.urlopen(target_url).read()
                dojo_api_inline_cache[target_url] = json.loads(data)
            
            info = dojo_api_inline_cache[target_url]

        except ValueError:
            error = self.state_machine.reporter.error(
                'The API Could not be fetched for %s' % api,
                literal_block(self.content, self.content))
            return [error]

        out = ""
        
        if showtitles:
            out = "\n========\nAPI Info\n========\n\n";
        
        if includelink:
            out += ":full API:\t%s%s\n" % ("http://dojotoolkit.org/api/", apislashed)
        
        if showsummary and "summary" in info:
            out += ":summary:\t%s\n" % info["summary"]
        
        if showreturns and "returns" in info:
            out += ":returns:\t%s\n" % info["returns"]
                
        out += "\n"

        sig = ""        
        if "type" in info and info["type"] == "Constructor":
            out += ".. api-inline :: %s\n\t:no-titles:\n\t:signature:\n\t:constructor:\n\n" % ( apidotted + ".constructor")

        if "parameters" in info and (showsignature or showlongsignature):
            if showtitles:
                out += "Parameters\n----------\n\n"
            
            # determine if ClassLike and add a `new `
            if ":constructor:" in arguments:
                sig += "var thing = new "
                apidotted = apidotted[:-12]
                
            sig += apidotted + "("
            tab = ""
            
            for param in info["parameters"]:
                
                type = param.get("type")
                name = param.get("name")
                desc = param.get("description", "").strip()
                body = "".join(desc.split("\n"))
                
                tab += "* **%s** `%s`\n\t\t\%s\n" % ( name, type, body )
                sig += " /* %s */ %s, " % ( type, name )
            
            sig = sig[:-2] + ")"
            
            if showsignature:
                out += "Signature\n\n.. js ::\n\n\t%s\n\n" % sig
        
            if showlongsignature: 
                out += "Overview\n\n%s\n" % tab
            
        
        if showexamples and "examples" in info:
            
            if showtitles:
                out += "Examples\n---------\n\n"
                
            for example in info['examples']:
                parts = example.split("\n")
                intabs = False
                for part in parts:
                    part = part.rstrip()
                    if part.startswith("\t\t"):
                        if not intabs:
                            # make a new tab block
                            intabs = True
                            out += "\n\n.. js ::\n\n%s\n" % part
                        else:
                            # keep just pumping
                            # if part.endswith("\n"): part = part[:-1]
                            out +=  "%s\n" % part

                    # make a new text block
                    else:
                        if intabs: out += "\n\n"
                        out += "%s\n" % part.strip()
                        intabs = False
                        
                out += "\n"

        if showproperties and "properties" in info:
            if ":showproperties:" in arguments:
                only = arguments[":showproperties:"]
                print only
            
            if showtitles:
                out += "Properties\n----------\n\n"
                
            for prop in info["properties"]:
                """"""
                print "%s \n %s \n" % (prop, info["properties"][prop])


        if showmethods and "methods" in info:
            
            if showtitles:
                out += "Methods\n-------\n\n"
            
            for method in info["methods"]:
                """"""

        #out += "</pre>"
        
        print out;
        
        try:
            lines = statemachine.string2lines(out)
            self.state_machine.insert_input(lines, "/")
        except SystemMessage:
            print "fooooooo"

        return []

# define a `ref:` role for reST, so Sphinx links turn back to wiki links:
def ref_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    # match :ref:`Bar! <link/link/link>` from rawText
    p = re.search('`(.*) <(.*)>`', rawtext)
    if(p):
        return [nodes.reference(rawtext, p.group(1), refuri="/" + p.group(2), **options)], []   
    else:
        return [], []
    # also, this could be safer:

def sample_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    """
        simple role matching :sample:`shit`, converting it to an inline <span> with a class
    """
    

class DojoHTMLWriter(Writer):
    """
    This docutils writer will use the DojoHTMLTranslator class below.
    """
    def __init__(self):
        Writer.__init__(self)
        self.translator_class = DojoHTMLTranslator

class DojoHTMLTranslator(HTMLTranslator):
    """
    Dojo-specific reST for the codeviewer stuff.
    """

    def visit_codeviewer(self, node):
        self.body.append('<div class="CodeGlassMiniRaw" label="%s" lang="%s"><textarea style="display:none">' % (node['label'], node['lang']))
        
    def depart_codeviewer(self, node):
        self.body.append('</textarea></div>')
        
    def visit_codeviewer_compound(self, node):
        # testing. switch to CodeGlass.base and require() it for backwards compat for now
        self.body.append('<div dojoType="docs.MiniGlass" class="CodeGlassMini" type="%s" pluginArgs="{djConfig:\'%s\', version:\'%s\'}" width="%s" height="%s" toolbar="%s"><div class="CodeGlassMiniInner">' % (
            node['type'].lower(),
            node['djconfig'],
            node['version'],
            node['width'],
            node['height'],
            node['toolbar'])
        )

    def depart_codeviewer_compound(self, node):
        self.body.append('</div></div>')
        
    # Don't apply smartypants to literal blocks
    def visit_literal_block(self, node):
        HTMLTranslator.visit_literal_block(self, node)
    
    def depart_literal_block(self, node):
        HTMLTranslator.depart_literal_block(self, node)

class codeviewer(TextElement): pass
class codeviewer_js(TextElement): pass
class codeviewer_css(TextElement): pass
class codeviewer_html(TextElement): pass
class codeviewer_compound(General, Element): pass

# Additional directive to output an example/source viewer
def _codeviewer(name, arguments, options, content, lineno, 
               content_offset, block_text, state, state_machine):

    raw = u'\n'.join(content)

    language = "html"
    if len(arguments) > 0:
        language = arguments[0]
        if language == "js":
            language = "javascript"
    
    try:
        lexer = get_lexer_by_name(language)
    except ValueError:
        # no lexer found - use the text one instead of an exception
        lexer = TextLexer()
        
    formatter = HtmlFormatter(noclasses=False, style='fruity')
    code = highlight(raw, lexer, formatter)
                
    label = ""
    if 'label' in options:
        label = options['label']
    
    mycode = codeviewer(raw, raw)
    mycode['lang'] = language
    mycode['label'] = label
    
    # returns both the highlighted text, and the codeviewer code (which goes through visit_codeviewer)
    # codeviewer code is hidden. highlighted is in it's place.
    return [nodes.raw('', code, format='html'), mycode]
    

def _codeviewer_js(name, arguments, options, content, lineno, 
               content_offset, block_text, state, state_machine):
    return _codeviewer(name, ['js'], options, content, lineno, 
               content_offset, block_text, state, state_machine)

def _codeviewer_css(name, arguments, options, content, lineno, 
               content_offset, block_text, state, state_machine):
    return _codeviewer(name, ['css'], options, content, lineno, 
               content_offset, block_text, state, state_machine)

def _codeviewer_html(name, arguments, options, content, lineno, 
               content_offset, block_text, state, state_machine):
    return _codeviewer(name, ['html'], options, content, lineno, 
               content_offset, block_text, state, state_machine)

# a more complex compounded component (so we can separate our code-blocks)
def _codeviewer_compound(name, arguments, options, content, lineno,
             content_offset, block_text, state, state_machine):
    
    text = '\n'.join(content)
    if not text:
        error = state_machine.reporter.error(
            'The "%s" directive is empty; content required.' % name,
            literal_block(block_text, block_text), line=lineno)
        return [error]
    node = codeviewer_compound(text)
    djconfig = "parseOnLoad: true"
    if 'djconfig' in options:
        djconfig = options['djconfig']
    node['djconfig'] = djconfig
    width = "700"
    if 'width' in options:
        width = options['width']
    node['width'] = width
    height = "400"
    if 'height' in options:
        height = options['height']
    node['height'] = height
    type = "dialog"
    if 'type' in options and (options['type'].lower() == 'inline'):
        type = "inline"
    node['type'] = type
    version = ""
    if 'version' in options:
        version = options['version']
    node['version'] = version
    toolbar = ""
    if 'toolbar' in options:
        toolbar = options['toolbar']
    node['toolbar'] = toolbar
    state.nested_parse(content, content_offset, node)
    return [node]

# all the available codeglass options need defined here?
masterOptions = { 
    'toolbar': lambda x: x, 
    'version': lambda x: x,
    'width': lambda x: x,
    'height': lambda x: x,
    'djconfig': lambda x: x,
    'theme': lambda x: x,
    'type': lambda x: x
}
    
# Directive is either new-style or old-style
clstypes = (type, types.ClassType)
def add_directive(name, obj, content=None, arguments=None, **options):
    if isinstance(obj, clstypes) and issubclass(obj, rst.Directive):
        if content or arguments or options:
            raise ExtensionError('when adding directive classes, no '
                                 'additional arguments may be given')
        directives.register_directive(name, directive_dwim(obj))
    else:
        obj.content = content
        obj.arguments = arguments
        obj.options = masterOptions
        directives.register_directive(name, obj)

# the main extensions
add_directive('js', _codeviewer_js, 1, (0, 1, 0), label=lambda x: x)
add_directive('javascript', _codeviewer_js, 1, (0, 1, 0), label=lambda x: x)
add_directive('css', _codeviewer_css, 1, (0, 1, 0), label=lambda x: x)
add_directive('html', _codeviewer_html, 1, (0, 1, 0), label=lambda x: x)

# deprecated syntax:
add_directive('cv', _codeviewer, 1, (0, 1, 0), label=lambda x: x) #deprecated
add_directive('codeviewer', _codeviewer,  1, (0, 1, 0), label=lambda x: x) #deprecated  

add_directive('code-example', _codeviewer_compound, 1, (0, 0, 0))
#deprecated
add_directive('codeviewer-compound', _codeviewer_compound, 1, (0, 0, 0)) # deprecated
add_directive('cv-compound', _codeviewer_compound, 1, (0, 0, 0)) # deprecated

# Simple dojoisms
directives.register_directive('live-code', LiveCode)
directives.register_directive('api-link', DojoApi)    
directives.register_directive('api-inline', DojoApiInline)
register_canonical_role('ref', ref_role);

# TODO: DO WE STILL NEED THIS CODE?
def add_node(node, **kwds):
    nodes._add_node_class_names([node.__name__])
    
add_node(codeviewer)
add_node(codeviewer_compound)
