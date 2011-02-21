"""
    Pygments directives for code-block highlighting
"""

import types, re, dojo

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

from docutils import nodes, utils
from docutils.nodes import literal_block, TextElement, FixedTextElement, Element, General
from docutils.parsers import rst
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.roles import register_canonical_role
from docutils.writers.html4css1 import HTMLTranslator, Writer

# Options
# ~~~~~~~

# Set to True if you want inline CSS styles instead of classes
INLINESTYLES = False
STYLE = "fruity"

# The default formatter
DEFAULT = HtmlFormatter(noclasses=INLINESTYLES, style=STYLE)

# Add name -> formatter pairs for every variant you want to use
VARIANTS = {
    'linenos': HtmlFormatter(noclasses=INLINESTYLES, linenos=True),
}

class Pygments(Directive):
    """ Source code execution.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = dict([(key, directives.flag) for key in VARIANTS])
    has_content = True

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()
        # take an arbitrary option if more than one is given
        formatter = self.options and VARIANTS[self.options.keys()[0]] or DEFAULT

        #  print >>open('pygments.css', 'w'), formatter.get_style_defs('.highlight')
        parsed = highlight(u'\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]

directives.register_directive('sourcecode', Pygments)
directives.register_directive('code-block', Pygments)
directives.register_directive('code', Pygments)
