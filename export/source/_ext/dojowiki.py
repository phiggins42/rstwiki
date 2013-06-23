# -*- coding: utf-8 -*-

"""
    Small shim loading rstWiki dojo.py to register directive, and providing duplicate DojoHtmlTranslator
    class that subclasses SmartyHtmlTranslator instead
"""


from docutils.nodes import literal_block, TextElement, Element, General
from docutils.parsers.rst import directives
import docutils, sys, os
from sphinx.writers.html import SmartyPantsHTMLTranslator

# this registers all the same roles the rstwiki supports
import dojo


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
        self.body.append('<div data-dojo-type="docs.MiniGlass" class="CodeGlassMini" data-dojo-props="type: \'%s\', pluginArgs:{ dojoConfig: \'%s\', version:\'%s\' }, width:\'%s\', height:\'%s\', toolbar:\'%s\', themename:\'%s\'"><div class="CodeGlassMiniInner">' % (
            node['type'].lower(),
            node['djconfig'],
            node['version'],
            node['width'],
            node['height'],
            node['toolbar'],
            node['theme'])
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
    """
        This is just a placeholder so Sphinx thinks this is a genuine extension.
        All the directives are registered by importing dojo module from rstwiki
    """
