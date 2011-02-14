#
#   rstwiki config stuffs
#
wiki = {
    
    # sample svn repo
    #"SRC_VCS": "svn",
    #"SRC_REPO": "https://svn.dojotoolkit.org/dojo_doc_wiki/_source-moin/",
    #"RST_ROOT":"./svn_sample_repo/",

    # sample git repo
    #"SRC_VCS":"git",
    #"SRC_REPO": "git://github.com/phiggins42/rstwiki-git.git",
    #"RST_ROOT":"./git_sample_repo/",
    
    # sample local repo
    "SRC_VCS": "local",
    "SRC_REPO":"",
    "RST_ROOT":"./sample_data/",
    
    # set to `True` if wanting to do simple auth against an LDAP server
    "USE_LDAP": False,
    
    # set to `False` if you want to manually push/commit changes, or if local
    "COMMIT_ONSAVE": True,
    
    # if serving directly, listen on this port
    "LISTEN_PORT": 4200,
    
    # where files served from /_static/ root live
    # note: it's probably better to proxypass this or the like
    "STATIC_ROOT": "./_static/",
    "STATIC_ALIAS": "/_static"
}

# add our src/ tree to the import path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import directives