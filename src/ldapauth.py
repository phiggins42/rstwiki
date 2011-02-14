"""
    Simple auth against ldap
"""

import ldap, sys

def isuser(uname, pw):
    
    user = "uid=" + uname + ",ou=people,dc=dojotoolkit,dc=org"
    
    try: 
        
        con = ldap.initialize("ldap://localhost:389")
        con.simple_bind_s( user, pw )
        return True

    except ldap.SERVER_DOWN:
        print "Should we try to re-establish our tunnel somehow? root needs to do that..."
        return False

    except ldap.INVALID_CREDENTIALS, e:
        return False

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        print isuser(sys.argv[1], sys.argv[2]);