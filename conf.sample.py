#
#   rstwiki config stuffs
#
wiki = {

    # where the .rst tree will live. /sample_data/ has some test .rst. 
    # Suggest changing this to your own empty path to start editing 
    # "homepage" (/index.rst) 
    "RST_ROOT":"./sample_data/",
    
    # enum(git, svn, local)
    "SRC_VCS": "local",
    
    # ignored if SRC_VCS is local
    # if svn, commit happens directly on tree
    # if git, commit happens direclly tree (?)
    "SRC_REPO": "{some github|svn repo}",
    
    # set to `True` if wanting to do simple auth against an LDAP server
    "USE_LDAP": False,
    
    # set to `False` if you want to manually push/commit changes, or if local
    "COMMIT_ONSAVE": True,
    
    # if serving directly, listen on this port
    "LISTEN_PORT": 4200,
    
    # where files served from /_static/ root live
    # note: it's probably better to proxypass this or the like
    # note: also, change this to ./_static/release/ after a default build.sh
    # if serving from the app directly. Else adjust your ProxyPass path, etc.
    "STATIC_ROOT": "./_static/"
    
}

# add our src/ tree to the import path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

if wiki['USE_LDAP']: import ldapauth as auth
import directives
