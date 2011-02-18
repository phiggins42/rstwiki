#!/usr/bin/env python
# encoding: utf-8
"""
docserver.py - the core of the rst processing nonsense.

"""
import subprocess, codecs, re, sys, os, urllib, cgi
import cgitb; 
import SimpleHTTPServer
from docutils import core, io
from dojo import DojoHTMLWriter
from conf import wiki as conf
from Crumbs import Crumbs as crumbs
from locks import Locker
import Cookie, random, string
from admin import getChanges
import time
from threading import Timer
import threading
import urllib

# session id generator
chars = string.ascii_letters + string.digits
all_sessions = {}
class SessionElement(object): pass
def makesessionid(length):
    return ''.join([random.choice(chars) for i in range(length)])

# make this scan *.html in templates/ and map to some convention?
# also maybe poll them for changes and invalidate stuff. 
master_template = open("templates/master.html", "r").read()
edit_template = open("templates/editform.html", "r").read()
login_template = open("templates/login.html", "r").read()
upload_template = open("templates/upload.html", "r").read()
admin_template = open("templates/admin.html", "r").read()

# for git queuing
pushScheduled = threading.Event();

# validated user cache, per restart
authed_users = {}

class DocHandler (SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    server_version = "rstWiki/0.1a"
    user = "anonymous"
    def Session(self):
        if self.cookie.has_key("sessionid"):
            sessionid = self.cookie['sessionid'].value
        else:
            sessionid = makesessionid(8)
            self.cookie['sessionid'] = sessionid
        try:
            sessionObject = all_sessions[sessionid]
        except KeyError:
            sessionObject = SessionElement()
            all_sessions[sessionid] = sessionObject
        return sessionObject
        
    def userisauthorized(self):
        """
            a fast return for authorization status for this user/request. actual auth lookup should
            only be done once
        """
        ret = True
        if conf['USE_LDAP']:
            ret = False
            if self.cookie.has_key("sessionid"):
                id = self.cookie['sessionid'].value
                if id in authed_users:
                    ret = self.user == authed_users[id]
            else:
                ret = False

        return ret
        
    def wraptemplate(self, **kwargs):
        return self.filltemplate(master_template, **kwargs)
        
    def filltemplate(self, template, **kwargs):
        return re.sub("{{(.*)}}", lambda m: kwargs.get(m.group(1), ""), template)

    def checkuser(self):
        """
            update self.user if this request indicates this user is not a user
        """
        self.cookie = Cookie.SimpleCookie()
        if self.headers.has_key("cookie"):
            self.cookie = Cookie.SimpleCookie(self.headers.getheader("cookie"))

        self.info = self.Session()
        if self.cookie.has_key("sessionid"):
            sessionid = self.cookie['sessionid'].value
            if sessionid in authed_users:
                self.user = authed_users[sessionid]
            else:
                # sessionid == cookie.sessionid means they aren't a valid user
                self.user = self.cookie['sessionid'].value
        
    def do_GET(self):
        
        self.checkuser()
        self.do_process()

    def do_process(self):

        try:
            
            # static files should never be served from here. this is just a router for non
            # static files. path will be something like one of the following:
            #
            # /                 becomes /index
            # /dojo             becomes /dojo/index
            # /dojo/foo-bar     becomes /dojo/foo-bar but parented by /dojo/foo 
            # /dojo/index       becomes /dojo/index
            # /edit/dojo/       becomes /edit/dojo/index
            # /edit/dojo/index  becomes /edit/dojo/index
            # /edit/index       becomes /edit/index
            # /edit/            becomes /edit/index
            # /dojo/byId        becomes /dojo/byId
            # /dijit/form/Form  becomes /dijit/form/Form
            # /do/*            becomes /adm/*
            # /_static/*         should be served by proxy, shared with ref-guide _static
            # /*.jpg            images attached to wiki
            
            path = self.path
            editing = False
            passthru = False
            action = ""
            
            if path.startswith("/unlock/"):

                path = path[7:]
                file = rstfile(path)
                lock = Locker(file)
                if lock.islocked() and lock.ownedby(self.user):
                    lock.unlock()
                    self.do_serv(response=200, body="unlocked")
                else:
                    self.do_serv(response=500, body="failed")
                return;

            if path.startswith("/admin/"):
                self.do_serv(**self.runAdmin(path))
                return
            
            if path.startswith("/do/"):
                # return quickly for adm paths
                self.do_serv(**self.specialhandler(path))
                return

            if path.startswith("/search/"):
                self.do_serv(**self.runSearch(path))
                return
            
            if path.startswith("/login"):
                self.do_serv(**self.loginform(path))
                return
            
            if path.startswith("/upload"):
                self.do_serv(**self.uploadform(path))
                return
                
            # else, fix up the url a tad    

            if path.startswith("/edit/"):
                # we're editing a file. strip "/edit" from the path and flag it
                path = path[5:] 
                editing = True
                action = "Editing"

            # local static files included in this app folder
            if path.startswith(conf['STATIC_ALIAS']):
                passthru = True;
                file = conf['STATIC_ROOT'] + path[len(conf['STATIC_ALIAS']):]
                # unset the cookie values? they're tiny tho

            # if we're the root, always add `index`
            if path == "/" or path.endswith("/"): path += "index" #actually should check path[:-1].rst before adding index if non rooted item
            parts = path.split("/")
            
            # files in the root need to be += index (djConfig, others in root don't follow this :/)
            # if len(parts) == 2 and parts[1] != "site.css":
            #    path += "/index";

            # wiki referenced image handling. all are in source tree:
            # note, static url's won't make it this far by way of ProxyPass from apache
            # also there are a lot more type of images than these three. expand this support:
            if path.endswith("jpg") or path.endswith("png") or path.endswith("gif"):
                file = conf['RST_ROOT'] + path
                passthru = True
            elif not passthru:
                file = rstfile(path)
                        
            if(passthru):
                # direct LINK. always 200 sadly?
                if not os.path.exists(file):
                    self.do_serv(response=404)
                else:    
                    self.do_serv(response=200, body=open(file).read(), raw=True)
                return
            
            if(not os.path.exists(file)):
                out = ".. _" + path[1:] + ":\n\nTitle\n====="
                action = "Creating"
                editing = True
            else: 
                out = read_file(file)

            crumbs = makenavcrumbs(path);
            if(not editing):
                stuff = self.wraptemplate(
                    root = conf['STATIC_ALIAS'], 
                    title = action + " " + path, 
                    crumbs = crumbs, 
                    body = parse_data(path, out), 
                    nav = self.editlink(path)
                )
            else:
                filelock = Locker(file)
                locked = filelock.islocked()
                if locked and not filelock.ownedby(self.user):
                    stuff = self.wraptemplate(
                        title="File Locked", 
                        crumbs = crumbs, 
                        body = "<h3>Locked</h3><p>Can't edit for another " + str(filelock.expiresin()) + " seconds</p><p><em>owner:</em> " + filelock.owner(), 
                        root = conf['STATIC_ALIAS']
                    )
                else:
                    filelock.lock(self.user)
                    editcontent = self.filltemplate(edit_template, path=path, body=out, root=conf['STATIC_ALIAS'])
                    stuff = self.wraptemplate(
                        title = action + " " + path, 
                        crumbs = crumbs, 
                        body = editcontent, 
                        root = conf['STATIC_ALIAS']
                    ) 
                        
            self.do_serv( body = stuff, headers = { "Content-type":"text/html" } );
                
        except IOError:
            self.do_serv(response=500, body="oops. internal error.")
    
    def do_POST(self):
        """
            Incoming POST could mean login(?) or save to page. /edit/ has been stripped. It'll always be /login or /a/b/c
        """
        try:
            
            self.checkuser()
            
            # determine auth, and path.
            #  incoming post data is allegedly replacement for existing .rst of that name

            ctype, pdict = cgi.parse_header(self.headers.getheader("Content-type"))
            if ctype == "multipart/form-data":
                params = cgi.parse_multipart(self.rfile, pdict)
            else:
                print ctype
                size = int(self.headers['Content-length'])
                if size > 0:
                    incoming = self.rfile.read(size)
                    params = parse_post(incoming)
                else:
                    params = {}

            path = self.path
                
            if "login" in params:
                # if they are senging uname/pw pairs lets try to log them in now
                # before we process the upload/update/etc
                if(conf['USE_LDAP']):
                    from ldapauth import isuser
                    sessionid = self.cookie['sessionid'].value
                    if isuser(params['uname'], params['pw']):
                        authed_users[sessionid] = params['uname']
                        self.checkuser()
            
            if "upload" in params:
                # we need to explode off the last part of the path and put files in that folder
                # also it appears I can't find the content-disposition:filename="" part of the multipart? ugh.
                print "incoming files for", path 
                for item in params:
                    print "key:", item, "size:", len(params[item][0]), "bytes"

            if "content" in params:
                                
                file = rstfile(path)
                # ugh. check lock. and owner of the lock.
                filelock = Locker(file)
                locked = filelock.islocked() 
                if not locked or locked and filelock.ownedby(self.user):
                
                    if(size > 0 and self.userisauthorized()):
                        isNewFile = False
                        data = params['content'].rstrip()
                        dir = os.path.dirname(file)
                        if not os.path.exists(dir):
                            os.makedirs(dir)
                  
                        if not os.path.exists(file): 
                            isNewFile=True


                        print >>open(file, 'w'), data
                        file = file[len(conf["RST_ROOT"])+1:]
                        if "message" in params and params["message"]!="":
                            message =  params["message"]
                        else:
                            if isNewFile:
                                 message = 'Added ' 
                            else:
                                 message = 'Updated ' 

                            message = message + path + ' via wiki from [' + self.user + ']'
                       
                        # break this into a vcs-adaptor API with local,git,and svn default adaptors
                        # eg: api = VcAdapter(conf['src_vcs'])
                        # api.addFile(file); api.commit(file, message); api.moveFile(file, newfile);
                        
                        vcs = conf["SRC_VCS"]
                        if vcs == "git":
                            from git import Repo,GitCmdObjectDB
                            """
                                git add {file}
                                git commit {file} -m "updates from [{user}] via wiki"
                            """
                            
                            repo = Repo(conf["RST_ROOT"],odbt=GitCmdObjectDB) 
                            git=repo.git
    
             
                            if isNewFile:
                                git.add(file)          
                            res = git.commit(file,
                                message = message, 
                                author="\"" + self.user + " <" + self.user + "@wiki.dojotoolkit.org>\""
                            );

                            def push():
                                print "Pushing commits to remote write branch."
                                # i think this would be the intent of COMMIT_ONSAVE when VCS==git, eg:
                                # we may want to avoid pushing at all with a switch. or do it from cron
                                pushScheduled.clear()

                                git.push(repo.remotes.origin)

                                """
                                msg = urllib.urlencode({
                                     "pull[base]": "master",
                                     "pull[head]": "dmachi:master",
                                     "pull[title]": "Pull request for updated wiki docs",
                                     "pull[body]": "Pull request for updated wiki docs"
                                })
                                urllib.urlopen("https://github.com/api/v2/json/pulls/phiggins42/rstwiki-git", msg)
                                """

                                pushScheduled.clear()
                                
                            if not pushScheduled.isSet():
                                if "SRC_PUSH_DELAY" in conf and conf["SRC_PUSH_DELAY"]>0:
                                    pushScheduled.set() 
                                    pushGit = Timer(conf["SRC_PUSH_DELAY"], push)
                                    pushGit.start()
                                
                        elif vcs == "svn":
                            """
                                svn commit {file} -m "updates from [{user}] via wiki"
                            """
                            args = ["svn","commit", file, "-m", message]
                            print " ".join(args)
                            proc = subprocess.Popen(args, 4096);
                            data = proc.communicate()[0];
                            print data
                        
                        invalidate_key(path)
                        filelock.unlock()

            self.do_process();
            
        except IOError, e:
            print e
            self.do_serv(response=500)

    def runSearch(self, path):
        """
            Run a search for a term to be infered from the global `path` (/search has already been stripped)
            returns an object of values suitable for do_serv kwargs
        """

        term = path[1:].split("/")[1]
        proc = subprocess.Popen(["./search.sh", term], 4096, stdout=subprocess.PIPE)
        data = proc.communicate()[0]
        lines = data.split("\n")
        results = []

        for line in lines:
            # match out the filename and text snippet
            parts = re.search('^\.\.\/_source-moin\/(.*)\.rst:(.*)$', line)
            if parts:
                results.append(parts.group(1))

        tout = [];
        stuff = sorted(set(results))
        for link in stuff:
            tout.append("<li><a href='/" + link + "'>" + link + "</a></li>")

        return {
            "body": self.wraptempalte(
                body="<div><h2>Results for: " + term + "</h2><ul>" + "\n".join(tout) +  "</ul>",
                title= term
            ),
        }

    def specialhandler(self, path):
        """
            handle special /do calls. map commands to shell stuff and read the pipe.

            be careful.

        """
        cmd = path[1:].split("/")[1]
        args = [conf["SRC_VCS"], cmd];
        if(cmd == "push"):
            """
                double check auth here. don't allow this command unless project-committer
                oh also we only care if using vcs and auth. otherwise why the hell would
                they even be hitting this rpc
            """
        
        proc = subprocess.Popen(args, 4096, stdout=subprocess.PIPE, cwd=conf['RST_ROOT']);
        response = proc.communicate()[0]
        
        return {
            'body': self.wraptemplate(
                body = "<pre>" + cgi.escape(response) + "</pre>",
                title = "Execution output",
                root = conf["STATIC_ALIAS"]
            ),
            'headers':{
                "Content-type":"text/html"
            }
        }
    
    def uploadform(self, path):
        return {
            'body': self.wraptemplate(
                body = self.filltemplate(upload_template, path = path[8:]),
                title = "Upload",
                root = conf["STATIC_ALIAS"],
                crumbs = makenavcrumbs(path)
            ),
            'headers':{
                'Content-type':'text/html'
            }
        }

    def runAdmin(self, path):
        return {
            'body': self.wraptemplate(
                body = self.filltemplate(admin_template, path = path[8:], changes=getChanges()),
                title = "Administration",
                root = conf["STATIC_ALIAS"],
                crumbs = makenavcrumbs(path)
            ),
            'headers':{
                'Content-type':'text/html'
            }
        }
    
    def loginform(self, path):
        # FIXME: handle auth somehow
        return {
            'body': self.wraptemplate(
                body = self.filltemplate(login_template, path = path[7:]),
                title = "Login",
                root = conf["STATIC_ALIAS"],
                crumbs = makenavcrumbs(path)
            ),
            'headers':{
                "Content-type":"text/html"
            }
        }
    
    def editlink(self, path):
        if self.userisauthorized():
            return "<a href='/edit" + path + "'>edit</a>\
                <a href='/upload" + path + "'>upload</a>\
                "
        else:    
            return "<a id='loginanchor' href='/login" + path + "'>login</a>"
        
    def do_serv(self, **kwargs):
        """
            Sets all headers and serves whatever content it is told to.
        """

        raw = kwargs.get("raw", False)
        response = kwargs.get("response", 200)
        self.send_response(response)

        if "headers" in kwargs:
            for header in kwargs["headers"]:
                self.send_header(header, kwargs["headers"][header])

        for morsel in self.cookie.values():
            self.send_header('Set-Cookie', morsel.output(header='').lstrip())

        self.end_headers();

        body = kwargs.get("body", "")
        if not raw: body = body.encode("utf-8")
        
        self.wfile.write(body);

# these are all random helpers, and should be moved somewhere they are most appropriate

def rstfile(path):
    """
        return the .rst file associated with a given `path`
    """
    return conf['RST_ROOT'] + path + ".rst"

def read_file(filename):
    """
        shorthand for forcing utf8
    """
    if(os.path.exists(filename)):
        f = codecs.open(filename, "r", "utf-8")
        # f = open(filename)
        data = f.read()
        return data;

def makenavcrumbs(path):
    if(path.startswith("/")):
        path = path[1:]
    parts = crumbs(path);
    return "<div class='crumbs'><a href='/'>home</a> / " + " / ".join(parts.links()) + "</div>"

# FIXME: move to a simple generic memory/disk/cache mech?
data_cache = {}

def invalidate_key(key):
    """
        Unset the memory data for the identifier (path)
    """
    if key in data_cache:
        del data_cache[key]

def _clearall():
    """
        Clear if repo changes? Clear if dojo.py changes? 
    """
    for key in data_cache:
        invalidate_key(key)

def parse_data(key, data):
    # FIXME: need to invalidate cache entry if file mtime is newer than last read. maybe in read_file?
    if not key in data_cache:
        data_cache[key] = core.publish_parts(
            source=data, source_path="/",
            destination_path="/", writer=DojoHTMLWriter(), settings_overrides={})
            
    return data_cache[key]['html_body'];

def rawlink(path):
    # this is kind of useless? add a [cancel] button to the editing form
    return "<a href='" + path + "'>rendered</a>"

def parse_post(data):
    """ Probably a better postdata-to-dict function somewhere...
    """
    parts = {}
    raw = data.split("&")
    for part in raw:
        k,v = part.split("=")
        parts[k] = urllib.unquote_plus(v)

    return parts
