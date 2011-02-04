"""
    Dojo specific rst/sphinx directives
"""

import types, re

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

from docutils import nodes, utils
from docutils.nodes import literal_block, TextElement, FixedTextElement, Element, General
from docutils.parsers import rst
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.roles import register_canonical_role
from docutils.writers.html4css1 import HTMLTranslator, Writer

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
        markup = "<p class='apiref'>API Rerence: <a target='_api' href='http://dojotoolkit.org/api/" + apislashed + "'>" + apidotted + "</a></p>"
        return [nodes.raw('', markup, format='html')]


# define a `ref:` role for reST, so Sphinx links turn back to wiki links:
def ref_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    # match :ref:`Bar! <link/link/link>` from rawText
    p = re.search('`(.*) <(.*)>`', rawtext)
    if(p):
        return [nodes.reference(rawtext, p.group(1), refuri="/" + p.group(2), **options)], []   
    else:
        return [], []
    # also, this could be safer:

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
        self.body.append('<div label="%s" lang="%s"><pre>' % (node['label'], node['lang']))
        
    def depart_codeviewer(self, node):
        self.body.append('</pre></div>')
        
    def visit_codeviewer_compound(self, node):
        self.body.append('<div dojoType="CodeGlass.base" type="%s" pluginArgs="{djConfig:\'%s\', version:\'%s\'}" width="%s" height="%s" toolbar="%s">' % (
            node['type'].lower(),
            node['djconfig'],
            node['version'],
            node['width'],
            node['height'],
            node['toolbar'])
        )

    def depart_codeviewer_compound(self, node):
        self.body.append('</div>')
        
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
    code = u'\n'.join(content)
    language = "html"
    if len(arguments) > 0:
        language = arguments[0]
        if language == "js":
            language = "javascript"
    label = ""
    if 'label' in options:
        label = options['label']
    mycode = codeviewer(code, code)
    mycode['lang'] = language
    mycode['label'] = label
    return [mycode]

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
        obj.options = options
        directives.register_directive(name, obj)

# the main extensions
add_directive('js', _codeviewer_js, 1, (0, 1, 0), label=lambda x: x)
add_directive('javascript', _codeviewer_js, 1, (0, 1, 0), label=lambda x: x)
add_directive('css', _codeviewer_css, 1, (0, 1, 0), label=lambda x: x)
add_directive('html', _codeviewer_html, 1, (0, 1, 0), label=lambda x: x)
add_directive('code-example', _codeviewer_compound, 1, (0, 0, 0))

# deprecated syntax:
add_directive('cv', _codeviewer, 1, (0, 1, 0), label=lambda x: x) #deprecated
add_directive('codeviewer', _codeviewer,  1, (0, 1, 0), label=lambda x: x) #deprecated  #deprecated
add_directive('codeviewer-compound', _codeviewer_compound, 1, (0, 0, 0)) # deprecated
add_directive('cv-compound', _codeviewer_compound, 1, (0, 0, 0)) # deprecated

# Simple dojoisms
directives.register_directive('api-ref', DojoApi)    
register_canonical_role('ref', ref_role);

# TODO: DO WE STILL NEED THIS CODE?
def add_node(node, **kwds):
    nodes._add_node_class_names([node.__name__])
add_node(codeviewer)
add_node(codeviewer_compound)
