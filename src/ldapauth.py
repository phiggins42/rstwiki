"""
    Simple auth against ldap
"""
import inspect
import ldap, sys,cherrypy
import ldif
from StringIO import StringIO
from ldap.cidict import cidict

def isuser(uname, pw):

    ldapconf = cherrypy.request.app.config.get("ldap")

    if "base_dn" in ldapconf and ldapconf.get("base_dn") :
        user = "uid=%s,%s" % ( uname, ldapconf.get("base_dn") )
    else: 
        user = uname
        
    try:
        con = ldap.initialize(ldapconf.get("host","ldap://localhost"))

        UserObj = { 'uname': uname, 'groups': [] }
        #first bind as the user to make sure we can login
        con.simple_bind_s( user, pw )

        #if LDAP_BIND_USER is defined, rebind as that user to get some additional info
        bind_dn = ldapconf.get("bind_dn",None)

        if bind_dn is not None:
             admincon = ldap.initialize(ldapconf.get("host","ldap://localhost"))
             admincon.simple_bind_s(bind_dn,ldapconf.get("bind_password"))
             filter = "(uid=" + uname + ")"
             result = get_search_results(admincon.search_s(
                ldapconf.get("base_dn"), 
                ldap.SCOPE_SUBTREE, 
                filter, 
                ldapconf.get("user_attributes")
             ))[0];
             
             for key in result.get_attr_names():
                  UserObj[key] = result.get_attr_values(key)[0]

             filter = "(member=" + user + ")"
             groups = get_search_results(admincon.search_s(ldapconf.get("groupBaseDn"), ldap.SCOPE_SUBTREE, filter, ['cn']))

             for group in groups:
                 UserObj['groups'].append(group.get_attributes()["cn"][0])


        print "Logged In User: %s" % (UserObj)
        cherrypy.session["user"] = UserObj

        return True

    except ldap.SERVER_DOWN:
        print "Should we try to re-establish our tunnel somehow? root needs to do that..."
        return False

    except ldap.INVALID_CREDENTIALS, e:
        return False

def get_search_results(results):
    res = []
    if type(results) == tuple and len(results) == 2 :
        (code, arr) = results
    elif type(results) == list:
        arr = results

    if len(results) == 0:
        return res

    for item in arr:
        res.append( LDAPSearchResult(item) )
    return res

class LDAPSearchResult:
    dn = ''

    def __init__(self, entry_tuple):
        (dn, attrs) = entry_tuple
        if dn:
            self.dn = dn
        else:
            return

        self.attrs = cidict(attrs)

    def get_attributes(self):
        return self.attrs

    def set_attributes(self, attr_dict):
        self.attrs = cidict(attr_dict)

    def has_attribute(self, attr_name):
        return self.attrs.has_key( attr_name )

    def get_attr_values(self, key):
        return self.attrs[key]

    def get_attr_names(self):
        return self.attrs.keys()

    def get_dn(self):
        return self.dn


    def pretty_print(self):
        str = "DN: " + self.dn + "\n"
        for a, v_list in self.attrs.iteritems():
            str = str + "Name: " + a + "\n"
            for v in v_list:
                str = str + " Value: " + v + "\n"
                str = str + "========\n"
        return str

    def to_ldif(self):
        out = StringIO()
        ldif_out = ldif.LDIFWriter(out)
        ldif_out.unparse(self.dn, self.attrs)
        return out.getvalue()

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        print isuser(sys.argv[1], sys.argv[2]);
