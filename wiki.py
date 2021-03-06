#!/usr/bin/env python
# encoding: utf-8
"""
    teh root wiki logic
"""

import os, os.path,sys,cherrypy

# this code is path sensitive, so make sure we have the correct one
os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from auth import AuthController
from docserver import Wiki
from hooks import Github

#precompile templates
templatePath = os.path.join(os.path.dirname(__file__), "templates") 
if not os.system("cheetah compile -R %s --iext tmpl --nobackup --odir _templates" %(templatePath)):
   sys.path.append(os.path.join(os.path.dirname(__file__), "_templates/","templates"))
else:
   print "Failed to Compile Templates"
   exit(1)

#mount a couple of wikis, one at root and one /rstwiki  different configs for each
cherrypy.tree.apps[''] = Wiki('/', os.path.join(os.path.dirname(__file__), "wiki.conf"))
cherrypy.tree.apps['/rstwiki-howto'] = Wiki('/rstwiki-howto', os.path.join(os.path.dirname(__file__), "rstwiki_docs.conf"))
cherrypy.tree.apps['/github'] = Github('/github', os.path.join(os.path.dirname(__file__), "github.conf"))
#mount the auth app (login/logout), todo wrap this in an app when the AuthController gets a makeover
cherrypy.tree.mount(AuthController(),"/auth",os.path.join(os.path.dirname(__file__), "wiki.conf"))


#add files in the template dir to autoreload monitoring
for f in os.listdir(os.path.join(os.path.dirname(__file__),"templates")):
    cherrypy.engine.autoreload.files.add(os.path.join(os.path.dirname(__file__),"templates",f))

if __name__ == '__main__':
   cherrypy.config.update(os.path.join(os.path.dirname(__file__), 'global.conf'))
   cherrypy.engine.start()
   cherrypy.engine.block()
