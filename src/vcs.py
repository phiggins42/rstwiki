import os.path

class Git:
    repo = None
    def __init__(self, config):
        from git import Repo,GitDB,GitCmdObjectDB
        self.vcs=config.get('vcs')
        self.wiki = config.get('wiki') 
        print "Initializing Git..."
        print "    Check for existing Repo at %s" % (self.wiki['root'])
        if not os.path.isdir(self.wiki["root"]):
            print "    Cloning %s" % (self.vcs['repo'])
            Repo.clone_from(self.vcs["repo"],self.wiki["root"])
       
        print "    Found Repository"
        self.repo = Repo(self.wiki["root"],odbt=GitCmdObjectDB)

    def commit(self,filename,**kwargs):
        import git 
        author=None
  
        print "Committing file to GIT"    
        if "message" in kwargs:
            message=kwargs['message']
        else:
            message="Wiki Update to %s" %(filename) 

        if "author" in kwargs:
            author=kwargs["author"]

        print "message: %s" % (message)
        return
        try:
            print "Commit Filename: %s "%(filename)
            self.repo.git.commit(filename,message=message)
            print "%s Commit: %s  :: %s" % (author,filename,message)

            if self.vcs.get('push.enabled'):
                self.push()

        except IOError,e:
            print "Failed to commit to repository %s" %(e)
        
    def push(self, *args):
        print "Pushing latest commits to GIT origin: %s" %(self.repo.remotes.origin)
        self.repo.git.push(self.repo.remotes.origin)
