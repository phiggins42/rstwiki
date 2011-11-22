.. _index:

=============
rstWiki howto
=============

A simple reStructuredText based Wiki application. Get the code from: http://github.com/phiggins42/rstwiki 

.. contents ::
    :depth: 2
    
Yet another wiki?
=================

This one is simple. It serves a very specific purpose, though can be mangled very easily into something to suit 
your needs. 

rstWiki isn't a `real` wiki, it only pretends to be one. The content for the wiki is, very simply, decoded directly
from reST files on disk. Ideally, these reST files are stored in some form of VCS. rstWiki [will eventually] 
support both git and subversion. VC can be turned off to work directly, locally, or whatever. 

reST is a super powerful yet simple markdown syntax. 

The Basics
==========

The very most basic of syntax explanations:

Paragraphs are lines of text separated by a blank link. 
This will not become a new paragraph. 

But this will.

Formatting inline text: **bold** ... *less bold* ... ``code`` ... `emphasis` ... 

The above line is produced by the following rst::

    Formatting inline text: **bold** ... *less bold* ... ``code`` ... `emphasis` ... 

A handy reference guide is available: http://docutils.sourceforge.net/docs/user/rst/quickref.html

**note:** reST is whitespace sensitive, like most python things. All `directives`_ need consistent indention::

    .. js ::
    
        alert("I am 4 spaces indented from the first . in the previous directive");
        
    I align with the previous directive, and am not included in it.
    
    * list item 1
        * list item 1.1
        * list item 1.2
    * list item 2
        * list item 2.1
            * list item 2.1.1
    * list item 3

The above produces:

.. js ::

    alert("I am 4 spaces indented from the first . in the previous directive");
    
I align with the previous directive, and am not included in it.

* list item 1
    * list item 1.1
    * list item 1.2
* list item 2
    * list item 2.1
        * list item 2.1.1
* list item 3

Unlike Dojo Toolkit, the docs use 4 spaces for indention, so please do not mix spaces/tabs. 

Links
-----

You can link to external pages, internal pages, and sections within the same page. 

External links look like::

    `Text of Link <http://example.com/link.url.html>`_
    
This would become: `Text of Link <http://example.com/link.url.html>`_

Linking to other internal pages uses `ref` ::

    :ref:`Jump to Somewhere! <somewhere/else>`
    
This would become: :ref:`Jump to Dijit! <somewhere/else>`

Finally, it is possible to cross-reference sections internally. If the section heading is a single word, you can simply add a trailing underscore to the word::

    Jump to Links_

This would create a link back to a major section: Links_

To reference a multi-word section header, surround the words with **`** and add a following underscore::

    Jump to `the basics`_
    
This would become: Jump to `the basics`_ (notice the case insensitivity here. It is not possible to have two headings with the same wording, even if under different subheadings)

Pages
-----

Each page must contain some basic information. When creating a page via the wiki interface, some skeletal reST is injected for you. The first and most important is the first line, a location to your document::

    .. _foo/bar/baz:

The above would point to a file at foo/bar/baz.rst

Next, include a top-level page heading. It can be anything, and serves as the document title. Many Dojo pages simply use the module as the first title::

    ===========
    foo.bar.baz
    ===========
    
The number of ``=`` characters must be equal or greater than the length of the title.

Next, provide a ``contents`` directive, to auto generate links to the various subsections::

    .. contents ::
        :depth: 2
        
Then continue on adding subsections, separated by headings. Using a top/bottom bar for your first heading, you could use the following syntax for sub-headings::

    =====
    Title
    =====
    
    Section 1
    =========
    
    Section 1.1
    -----------
    
    Section 1.1.1
    ~~~~~~~~~~~~~
    
    Section 1.2
    -----------
    
    Text under section 1.2
    
    Section 2
    =========

    Text under section 2
    
The depth of the sections is relevant, and can be previewed in the table of contents (which uses embedded unordered-lists as output)

Directives
==========

rstWiki ships with a ``dojo.py`` collection of custom directives in addition to the standard formatting directives above. There 3 styles of code formatting names, shorthanded to ``js``, ``html``, and ``css``

To define a block of any of those type code snippets, include the following::

    .. js ::
    
        alert('this is code')
        
This will produce output like:

.. js ::

    alert('this is code')

Similarly for ``css`` and ``html``

.. css ::

    @import "/foo/bar/baz.css";
    #main { color: red }
    
.. html ::

    <div id="foobar"></div>
    
These three block types can be embedded in a ``code-example`` directive, which will produce a live/runnable example::

    .. code-block ::
    
        The Text between the blocks just renders inline.
        
        .. js ::
        
            require(["dojo/main", "dojo/ready"], function(dojo, ready){
                ready(function(){
                    alert("WE RAN");
                    dojo.byId("bar").innerHTML = "#winning";
                })
                
            });
        
        You don't have to put words about the subsections
            
        .. html ::
        
            <p id="bar">Test?</p>
            
        .. css ::
        
            #bar { color:green; }
            
The above example will produce

.. code-example ::

    The Text between the blocks just renders inline.
    
    .. js ::
    
        require(["dojo/main", "dojo/ready"], function(dojo, ready){
            ready(function(){
                alert("WE RAN");
                dojo.byId("bar").innerHTML = "#winning";
            })
            
        });
    
    You don't have to put words about the subsections
        
    .. html ::
    
        <p id="bar">Test?</p>
        
    .. css ::
    
        #bar { color:green; }
  
You can add opening script or style tags for the ``js`` and ``css`` blocks, but it is not necessary.

**TODO** fix/document parseOnLoad / iframe.onload / whatever. some examples need normalization

Hosted Dojo
===========

A [mostly] up to date Dojo checkout is available for reference in this site. (The ``code-example`` directive uses a custom module). Access it's relative location via the ``{{dataUrl}}`` string in any ``code-example``

For instance, to include an additional css file, @import it:

.. code-example ::

    .. js ::
    
        require(["dojo/ready"], function(ready){
            ready(function(){
                alert(" - {{dataUrl}} - ");
            })
        });
        
    .. css ::

        @import "{{dataUrl}}dojox/grid/resources/grid.css";

This is useful for referencing additional CSS (as shown), or using static resources available in a Dojo tree used for tests. ``countries.json`` comes to mind. 
    
Note: ``claro.css`` is always loaded.

Images
======

Images can be referenced by an ``image`` directive::

    .. image :: pathtoimage.png
    
The location is relative::

    .. image :: /logo.png
    .. image :: logo.png
    
The former will look for an image in the root of the document tree, whereas the latter will look for an image in the current directory.

Index Files
===========

Most files can map directly to a/b/c.rst == a.b.c pages. Some, however, would have conflicting filenames if placed on a case-sensitive filesystem. Consider the following 3 files::

    dijit/Tree.rst
    dijit/tree.rst
    dijit/tree/subpage.rst
    
In JavaScript it is perfectly legal to have both a ``dijit.Tree`` and ``dijit.tree`` object, though when extracted into a case sensitive filesystem, only one of ``Tree.rst`` and ``tree.rst`` survive.

The solution in this case is the use an ``index`` file. Classes win, namespaces get the ``index``. The above example should be moved/fixed to become::

    dijit/Tree.rst
    dijit/tree/index.rst
    dijit/tree/subpage.rst
    
Documents linking to the Class would do so with a normal link::

    :ref:`Checkout the Tree Class <dijit/Tree>`
    
But documents linking to additional ``dijit.tree`` namespace information would link to the index::

    :ref:`More about dijit.tree <dijit/tree/index>`
    
**note:** some existing files may not follow this pattern consistently, though all current namespace/file conflicts have been resolved. New files added should follow this pattern.

**note:** the wiki attempts to discover ``index.rst`` files automatically and does not include them in the breadcrumb [currently] unless explicitly linked to. This could cause pages to link properly in the wiki but not in export. FIXME/confusing

