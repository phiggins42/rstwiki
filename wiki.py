import conf, os

class RstWiki(object):
    
    def process_path(self, path):
        """
            assume we've been giving a path like /foo/bar/baz 
            return the rendered output so our server can do it's thing
        """
        return self.config['template']
    
    def setup_server(self):
        """ 
            Setup the server. I guess this is here to easily subclass or change so you can
            serve directly from app, via ProxyPass, or include a wsgi shim? Who knows.
        """
        print "Binding to port", self.config["LISTEN_PORT"]
        # start the server. 
        
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
        
    def load_files(self):
        """
            Read in templates and other things that need to be cached
            We can just cram shit into self.config dict I guess
        """
        self.config['template'] = open("templates/master.html", "r").read()
    
    def __init__(self, config):
        self.config = config
        self.init_data()
        self.load_files()
        self.setup_server()
        
if __name__ == "__main__":
    wiki = RstWiki(conf.wiki)