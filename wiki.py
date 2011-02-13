#!/usr/bin/env python
# encoding: utf-8
"""
    teh root wiki logic
"""

import conf, os, subprocess
from docserver import DocHandler
from BaseHTTPServer import HTTPServer

class RstWiki(object):
    
    init_tries = 0
    
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
        if self.init_tries > 1:
            raise BaseException("unable to even begin to serve a filesystem.")
            
        vcs = self.config['SRC_VCS']
        
        if not os.path.exists(self.config["RST_ROOT"]):
            print "init: No data found. Running init."
            if vcs == "local":
                args = []
                os.makedirs(self.config['RST_ROOT'])
            elif vcs == "git":
                from git import Repo
                print self.config["RST_ROOT"] + " does not exist.  Cloning " + self.config["SRC_REPO"] + " to " + self.config["RST_ROOT"]
                Repo.clone_from(self.config["SRC_REPO"],self.config["RST_ROOT"])
            elif vcs == "svn":
		print "SVN Checkout"
                args = ["svn","co", self.config["SRC_REPO"], self.config['RST_ROOT']];
                co = subprocess.Popen(args, 4096)
                print co.communicate()[0]
		print "SVN Checkout Done"

            self.init_tries += 1
            self.init_data();
        else:
            print "Found Data at [" + self.config['RST_ROOT'] + "]"
            if vcs=="git":
                from git import Repo

		#pull in upstream data from the Origin (remote) repo
                repo = Repo(self.config["RST_ROOT"])
		if not repo.is_dirty():
                    print "Updating local git repository from " + self.config["SRC_REPO"]
                    origin = repo.remotes.origin
                    origin.fetch()
                    origin.pull()
                else:
                    print "Not updating local git repository because it is_dirty()"
            
    def __init__(self, config):
        self.config = config
        self.init_data()
        print "Launching HTTP Server"
        self.setup_server()
        
if __name__ == "__main__":
    thewiki = RstWiki(conf.wiki)
