#!/usr/bin/env python
# encoding: utf-8
"""
    teh root wiki logic
"""

import os, os.path,sys,cherrypy
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from auth import AuthController
from docserver import DocServer

#precompile templates
templatePath = os.path.join(os.path.dirname(__file__), "templates") 
if not os.system("cheetah compile -R %s --iext tmpl --nobackup --odir _templates" %(templatePath)):
   sys.path.append(os.path.join(os.path.dirname(__file__), "_templates/","templates"))
else:
   print "Failed to Compile Templates"
   exit(1)

root = DocServer()
root.auth=AuthController()



cherrypy.tree.mount(root, "/", os.path.join(os.path.dirname(__file__), "wiki.conf"))
root.start()

if __name__ == '__main__':
   cherrypy.config.update(os.path.join(os.path.dirname(__file__), 'global.conf'))
   cherrypy.quickstart()
   cherrypy.engine.start()
