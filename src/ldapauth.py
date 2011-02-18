"""
    Simple auth against ldap
"""
import inspect
import ldap, sys
from conf import wiki as conf
import ldif
from StringIO import StringIO
from ldap.cidict import cidict

def isuser(uname, pw):
   
    if "LDAP_BASE_DN" in conf:
        user = "uid=" + uname + "," + conf["LDAP_BASE_DN"]
    else: 
        user = uname
    
    try:
        print "Connecting to " + conf["LDAP_HOST"]
        con = ldap.initialize(conf["LDAP_HOST"])

	UserObj = {}
        #first bind as the user to make sure we can login
        print "Simple LDAP Login : " + user
        con.simple_bind_s( user, pw )

        #if LDAP_BIND_USER is defined, rebind as that user to get some additional info
        if "LDAP_BIND_USER" in conf:
             print "re-binding as: " + conf["LDAP_BIND_USER"]
             admincon = ldap.initialize(conf["LDAP_HOST"])
             admincon.simple_bind_s(conf["LDAP_BIND_USER"],conf["LDAP_BIND_PASSWORD"])
             print "RE-bind-ed as " + conf["LDAP_BIND_USER"]             
             filter = "(uid=" + uname + ")"
             print "Search Filter: " + filter
             result = get_search_results(admincon.search_s(conf["LDAP_BASE_DN"], ldap.SCOPE_SUBTREE, filter, ['cn','dn','firstName','givenName','mail','githubUID']))[0];
             print result.pretty_print()
             UserObj = result.get_attributes()
             filter = "(member=" + user + ")"
             print "groupFilter: " + filter

             groups = get_search_results(admincon.search_s(conf["LDAP_GROUP_BASE_DN"], ldap.SCOPE_SUBTREE, filter, ['cn']))
             UserObj.groups = []

             for group in groups:
                 UserObj.groups.push(group.get_attributes()["cn"])

             print inspect.getmembers(UserObj.get("groups"))

        print user + " Logged in."
        return True

    except ldap.SERVER_DOWN:
        print "Should we try to re-establish our tunnel somehow? root needs to do that..."
        return False

    except ldap.INVALID_CREDENTIALS, e:
        return False

def get_search_results(results):
    res = []
    print "Getting Search Results"
    if type(results) == tuple and len(results) == 2 :
        (code, arr) = results
    elif type(results) == list:
        arr = results

    if len(results) == 0:
        print "No Search Results"
        return res

    for item in arr:
        res.append( LDAPSearchResult(item) )
    print "Found " + str(len(res)) + "results"
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
