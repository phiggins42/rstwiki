.. _index:

===========
rstWiki
===========

A simple reStructuredText based Wiki application. Get the code from: http://github.com/phiggins42/rstwiki 

.. contents ::

Yet another wiki?
----------------------------

This one is simple. It serves a very specific purpose, though can be mangled very easily into something to suit 
your needs. 

rstWiki isn't a `real` wiki, it only pretends to be one. The content for the wiki is, very simply, decoded directly
from reST files on disk. Ideally, these reST files are stored in some form of VCS. rstWiki [will eventually] 
support both git and subversion. VC can be turned off to work directly, locally, or whatever. 

reST is a powerful yet simple markdown syntax. 

But why not use [...]?
----------------------

Because it was too complicated. 

The Basics
----------

The very most basic of syntax explanations:

Paragraphs are lines of text separated by a blank link. 
This will not become a new paragraph. 

But this will.

Formatting inline text: **bold** ... *less bold* ... ``code`` ... `emphasis` ... 

A handy reference guide is available: http://docutils.sourceforge.net/docs/user/rst/quickref.html


Custom Directives
-----------------

reST is easily extensible. rstWiki ships a custom ``dojo.py`` module defining several custom directives. One 
custom directive included in the ability for reST to understand relative links similar to the way a wiki behaves. 
Sphinx uses these relative references to index content and generate the table of contents. 
eg: :ref:`this links to some internal wiki page "foo/bar" <foo/bar>`

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

Setup
-----

The wiki will run standalone, serving html-rendered-reST data from a configured root path and static files from a 
defined folder.

First clone and init the submodules for the wiki:

.. code :: shell

    git clone git://github.com/phiggins42/rstwiki.git rstwiki
    cd rstwiki && git submodule init && git submodule update

Rename the ``conf.sample.py`` to ``conf.py`` and edit as needed. Then run the server:

.. code :: shell

   mv conf.sample.py conf.py && vi conf.py
   chmod +x wiki.py
   ./wiki.py

The static files should be processed by Apache or similar. Using Apache/ProxyPass is easy. Run the wiki 
server on a specified local port, and proxy the requests to the application, intercepting requests to ``_static``

.. code :: xml

    <VirtualHost *:80>

        ServerName local.servername
        ProxyPass /_static !
        Alias /_static {pathTo}/rstwiki/_static
        ProxyPass / http://localhost:4200/
        ProxyPassReverse / http://localhost:4200/
        ProxyPreserveHost On
        
        <Directory {pathTo}/rstwiki/_static>
            Order allow,deny
            Allow from all
        </Directory>
    
    </VirtualHost>

Restart Apache and hit http://local.servername ... If the server is public, you may also want to include an 
Alias directive pointing to a robots.txt

If it doesn't start right up, you'll likely need to install some dependencies. 

Related Items
-------------

* python >= 2.6
* Sphinx
* docutils
* Pygments
* python-ldap
* git, svn
* CodeMirror
* CodeGlass
* Dojo, Dijit, Dojox
