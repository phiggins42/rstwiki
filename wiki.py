#!/usr/bin/env python
# encoding: utf-8
"""
    teh root wiki logic
"""

import conf, os
from docserver import DocHandler
from BaseHTTPServer import HTTPServer

class RstWiki(object):
    
    def setup_server(self):
        """ 
            Setup the server. I guess this is here to easily subclass or change so you can
            serve directly from app, via ProxyPass, or include a wsgi shim? Who knows.
        """
        try:
            server = HTTPServer(('', self.config["LISTEN_PORT"]), DocHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            server.socket.close()
        
    def init_data(self):
        """
            determine what the hell we need to do with the source folder
        """
        
        if not os.path.exists(self.config["RST_ROOT"]):
            print "error: data path doesn't exist"
            # local? fail. complain. die.
            # git: create a branch of the .git url
            # svn: svn co the url
            # self.init_data() check again? prevent looping.
        else:
            print "cool: data tree is there"
            # should we clear all locks on startup?
            
    def __init__(self, config):
        self.config = config
        self.init_data()
        self.setup_server()
        
if __name__ == "__main__":
    thewiki = RstWiki(conf.wiki)
