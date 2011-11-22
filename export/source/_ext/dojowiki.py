# -*- coding: utf-8 -*-

from docutils.nodes import literal_block, TextElement, Element, General
from docutils.parsers.rst import directives
import docutils, sys

sys.path.append("../../../src")
import dojo

from sphinx.writers.html import SmartyPantsHTMLTranslator

class DojoHTMLTranslator(SmartyPantsHTMLTranslator):
    """
    Dojo-specific reST for the codeviewer stuff.
    """

    def visit_codeviewer(self, node):
        self.body.append('<div class="CodeGlassMiniRaw" label="%s" lang="%s"><textarea style="display:none">' % (node['label'], node['lang']))
        #self.body.append('<div label="%s" lang="%s"><pre>' % (node['label'], node['lang']))
        self.no_smarty += 1
        #SmartyPantsHTMLTranslator.visit_literal_block(self, node)
    
    def depart_codeviewer(self, node):
        #SmartyPantsHTMLTranslator.depart_literal_block(self, node)
        self.no_smarty -= 1
        #self.body.append('</pre></div>')
        self.body.append('</textarea></div>')
        
    def visit_codeviewer_compound(self, node):
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
        self.no_smarty += 1
        SmartyPantsHTMLTranslator.visit_literal_block(self, node)
    
    def depart_literal_block(self, node):
        SmartyPantsHTMLTranslator.depart_literal_block(self, node)
        self.no_smarty -= 1

def setup(app):
    
    print "DojoDocs shim loaded"
