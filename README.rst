RstWiki - simple wiki/rst interface
===================================

RstWiki provides a simple standalone Wiki interface to a directory of .rst
(reStructuredText) files. These .rst files are the sources to a Sphinx
documentation instance. The interface is a simple rst-rendering application
with basic authentication and VCS integration.

Dependencies
------------

* Cheetah >= 2.4
* CherryPy >= 3.1.2
* Docutils >= 0.5
* Python >= 2.6
* Pygments >= 1.4

Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

* GitDB == 0.5.2 (required for VCS integration)
* GitPython >= 0.3.1 (required for VCS integration)
* python-ldap >= 2.4 (required for LDAP authentication)
* Sphinx >= 1.0
* Dojo, CodeGlass

Installation
------------

1. Run ``easy_install cheetah cherrypy docutils pygments gitdb==0.5.2 gitpython``
   to install dependencies
2. Copy ``wiki.sample.conf`` to ``wiki.conf`` and configure appropriately
3. Ensure the session storage directory exists (by default, this is
   ``/tmp/rstwiki_sessions``)
4. Run ``wiki.py``

Configuration
-------------

There are two major configuration files. Options that should be modified for
normal operation are listed below.

global.conf
~~~~~~~~~~~

::

  [global]
  server.socket_port - Listen for requests on this port.
  server.socket_host - Listen for requests on this IP address. Use 0.0.0.0 to
                       bind to all interfaces.
  tools.sessions.storage_type - Type of session storage to use. One of "ram",
                                "file", "postgresql".
  tools.sessions.storage_path - The directory to store session data when using
                                "file" storage type.
  tools.sessions.timeout - Session timeout, in seconds.

wiki.conf
~~~~~~~~~

::

  [/_static]
  tools.staticdir.dir - The absolute path to the ``_static`` directory.

  [wiki]
  root - The absolute path to the directory in which wiki data will be stored.
  enable_vcs - Whether or not to use a VCS when managing wiki entries. If this
               is True, GitDB and GitPython must be installed.
  editable - Whether or not wiki contents should be editable.

  [auth]
  type - Type of authentication to use. One of "ldap", "bypass".

  [vcs]
  type - The type of version control system to use. Currently, only "git" is
         supported.
  repo - The address of the repository used to store and retrieve wiki data.
  push.enabled - Whether or not to push to upstream when a commit is made to
                 the local repository.
  [api]
  base_url - The root URL for looking up api-doc directives.  *Note* that 
    there is an issue where when building the docs, this option is ignored
    and you currently have to manually set it in ``src/dojo.py``.

License
-------

AFL/New BSD. See `Dojo's <http://dojotoolkit.org/license>`_ LICENSE for details