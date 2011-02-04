RstWiki - simple wiki/rst interface
===================================

**note**: this doesn't actually do anything just yet. 

**bummer**: proper "toc" support would be rad:

.. contents ::
    :depth: 2

Goal
----

To provide a simple standalone Wiki interface to a directory of .rst (reStructuredText) files. These .rst files are the sources
to a Sphinx documentation instance. The interface is a simple rst-rendering application with basic authentication and VCS integration.

Requirements
------------

    * docutils >= 0.5 (use trunk)
    * python >= 2.4
    * Pygments >= 1.4 http://pypi.python.org/pypi/Pygments#downloads

Optional
~~~~~~~~

    * python-ldap 
    * git
    * svn
    * sphinx
    * dojo, CodeGlass

Process
-------

    * edit config.py
    * spin server
        * check rst tree
        * fetch or init rst tree
            * git? clone branch with r/w
            * svn? co url
    * server:
        * handle special urls: /edit /do /login and /_static
            * /edit == edit the associated .rst
            * /login == right.
            * /do == a series of REST type commands. do/update do/pullreq, etc
            * /_static maps to a static tree to serve
    * map http://us/a/b/c to $root/a/b/c.rst 
        * handle root items as root/index (eg: http://us/foo means foo/index.rst)
        * view page:
            * render in html
            * determine auth
                * provide edit link
        * edit page:
            * file exists
                * check lock
                    * expired: unlock file
                    * valid: block editing
                    * null
                        * lock file
                        * show edit interface
            * else
                * wants to create
                    * touch file with boilerplate
                    * lock file
                    * show edit interface
                * abort
                    * back to prev page?
                    * unlock
        * handle POST:
            * determine appropriate .rst
            * check lock
                * valid: deny
                * null/expired: permit
                    * save:
                        * git? add/commit/push
                        * svn? commit
                        * local? nada
            * serve current .rst/path as GET would

License
-------

AFL/New BSD. See `Dojo's <http://dojotoolkit.org/license>`_ LICENSE for details                       