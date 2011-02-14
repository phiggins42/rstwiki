.. _rstwiki/setup:

Advanced Setup
==============

.. contents ::

Trouble Getting Started
-----------------------



Proxy via Apache
----------------

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

LDAP Information
----------------

LDAP integration is crude, and specific to the Dojo Foundations's CLA system. You can't use it. Full support would be awesome. Always set this to False
