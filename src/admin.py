from git import Repo, GitDB
from conf import wiki as conf

def getChanges():
    vcs = conf["SRC_VCS"]
    if vcs == "git":
        repo = Repo(conf["RST_ROOT"], odbt=GitDB)
	commits = repo.iter_commits("master",None,max_count=10)
        msg=""
	for commit in commits:
	    msg += "Commit: <a href=\"/admin/commit/" + commit.name_rev	+ "\">" + commit.name_rev + "</a><br>"
            msg += "Author: " + commit.author.name + "<br>"
            msg += "Message: " + commit.message + "<br>"
            #msg += "Diff:<br><pre>" + diff + "</pre><br>"
            msg += "<br>"
        return msg
    return "No Changes"	
