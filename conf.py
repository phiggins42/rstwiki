#
#   rstwiki config stuffs
#

rst_root = "./data"
src_vcs = "local"

wiki = {
    "RST_ROOT": "../rstwiki-git/",           # where the .rst tree will live. /sample_data/ has some test .rst. Suggest changing this to your own
    "SRC_VCS": "local",                     # enum(git, svn, local)
    "SRC_REPO": "{some github url}",        # ignored if SRC_VCS is local
    "USE_LDAP": False,                      # set to `True` if wanting to do simple auth against an LDAP server
    "COMMIT_ONSAVE": True,                  # set to `False` if you want to manually push/commit changes, or if local
    "LISTEN_PORT": 4200,                    # if serving directly, listen on this port
    "STATIC_ROOT": "./_static/"             # where files served from /_static/ root
}

# add our src/ tree to the import path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

if wiki['USE_LDAP']: import ldapauth as auth
import directives