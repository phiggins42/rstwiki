import os.path
import pprint,inspect

#Git VCS class, instantiates a repo on __init_ and then methods can be called
class Git:
    repo = None
    def __init__(self, config):
        from git import Repo,GitDB,GitCmdObjectDB
        self.vcs=config.get('vcs')
        self.wiki = config.get('wiki') 
        self.shadowEnabled=False

        print "Initializing Git..."
        print "    Check for existing Repo at %s" % (self.wiki['root'])
        if not os.path.isdir(self.wiki["root"]):
            print "    Cloning %s" % (self.vcs['repo'])
            Repo.clone_from(self.vcs["repo"],self.wiki["root"])

        self.repo = Repo(self.wiki["root"],odbt=GitCmdObjectDB)

        if self.vcs.get("branch",None) is not None:
            self.checkoutBranch(self.vcs.get("branch"))

        if self.vcs.get("shadow_enabled",False):
            if self.vcs.get("shadow_root",None) is not None: 
                if not os.path.isdir(self.vcs.get("shadow_root")):
                    print "Cloning Shadow Repo"
                    Repo.clone_from(self.vcs["repo"],self.vcs.get("shadow_root"))

                self.shadow = Repo(self.vcs.get("shadow_root"))
                self.checkoutBranch(self.vcs.get("shadow_branch"),repo=self.shadow)                 

    def commit(self,filename,**kwargs):
        import git 
        author=None
  
        print "Committing file to GIT"    
        message=kwargs['message'] or "Wiki Update to %s" %(filename) 

        if "author" in kwargs:
            author=kwargs["author"]

        try:
            print "Commit Filename: %s "%(filename)
            self.repo.git.commit(filename,message=message)
            print "%s Git Commit: %s  :: %s" % (author,filename,message)

            if self.vcs.get('push.enabled'):
                self.push()

        except IOError,e:
            print "Failed to commit to repository %s" %(e)
        
    def push(self, *args):
        print "Pushing latest commits to GIT origin: %s" %(self.repo.remotes.origin)
        self.repo.git.push(self.repo.remotes.origin)

        if self.vcs.get("shadow_enabled",False): 
            self.mergeShadow()

    def add(self,*arg,**kwargs):
        import git 
        for filename in arg:
            try:
                print "Add File: %s "%(filename)
                self.repo.git.add(filename)

            except IOError,e:
                print "Failed to add file to repository %s" %(e)

    def mergeShadow(self):
        print "Merging Shadow"
        git = self.shadow  

        #checkout a copy of the wiki branch
        print "Checkout %s" % (self.vcs.get("branch"))
        self.checkoutBranch(self.vcs.get("branch"),repo=self.shadow)
        self.shadow.active_branch.pull()
        #switch back to master
        print "Checkout %s" % (self.vcs.get("shadow_branch"))
        self.checkoutBranch(self.vcs.get("shadow_branch"),repo=self.shadow)
        self.shadow.active_branch.pull()
        git.merge(self.vcs.get("branch"),self.vcs.get("shadow_master"))
        git.push() 

    def checkoutBranch(self,branch,**kwargs):
        print "checkout branch: %s" % (branch)
        if "repo" in kwargs:
            git = kwargs["repo"].git
            repo=kwargs['repo']
        else:  
            git = self.repo.git
            repo=self.repo
   
        print "Repo.active branch=%s" %(repo.active_branch)
        match=False
        if repo.active_branch.name != branch:
            try:
               b = repo.branches[branch]
            except IndexError, e:
               git.branch("-f",branch, "origin/%s" % (branch)) 
            finally:
               git.checkout(branch)
