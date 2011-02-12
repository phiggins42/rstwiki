.. _rstwiki/directives:

Directives
==========

.. contents ::

Sample
------

The code for the custom directive is simple:

.. code :: python
    :linenos:
    
    import re
    from docutils import nodes
    from docutils.parsers.rst.roles import register_canonical_role
    
    def ref_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
        # match :ref:`Bar! <link/link/link>` from rawText
        p = re.search('`(.*) <(.*)>`', rawtext)
        if(p):
            return [nodes.reference(rawtext, p.group(1), refuri="/" + p.group(2), **options)], []   
        else:
            return [], []

    register_canonical_role('ref', ref_role);

Other more complex directives can be generated as well, returning either the rendered HTML to include in the 
output, or simply injecting formatted reST into the parser stream when encountering a directive. 

For example, the ``.. api-inline ::`` directive will fetch JSON data from the Dojo Toolkit API documentation 
export and attempt to inject it into the parser stream. See :ref:`more api-inline examples <foo/inline>` for tests.
