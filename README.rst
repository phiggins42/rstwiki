RstWiki - simple wiki/rst interface
===================================

**bummer**: proper "toc" support would be rad:

.. contents ::
    :depth: 2

Goal
----

To provide a simple standalone Wiki interface to a directory of .rst (reStructuredText) files. These .rst files are the sources
to a Sphinx documentation instance. The interface is a simple rst-rendering application with basic authentication and VCS integration.

Requirements
------------
    * cherrypy >= 3.1.2 http://cherrypy.org/
    * docutils >= 0.5 (use trunk)
    * python >= 2.6
    * Pygments >= 1.4 http://pypi.python.org/pypi/Pygments#downloads
    * CheetahTemplates >= 2.4
    
Optional
~~~~~~~~

    * python-ldap 
    * git
    * sphinx
    * dojo, CodeGlass


License
-------

AFL/New BSD. See `Dojo's <http://dojotoolkit.org/license>`_ LICENSE for details                       

Installation
------------

* edit wiki.sample.conf, adjusting paths as need be. rename to wiki.conf
* mkdir /tmp/rstwiki_sessions # from global.conf

* easy_install cherrypy
* easy_install docutils

* git clone https://github.com/cheetahtemplate/cheetah.git
    * easy_install ./cheetah/
    
* if using ldap, start a tunnel:
    
    
