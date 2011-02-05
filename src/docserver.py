#!/usr/bin/env python
# encoding: utf-8
"""
docserver.py - the core of the rst processing nonsense.

"""
import subprocess, codecs, re, sys, os, urllib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from docutils import core, io
from dojo import DojoHTMLWriter
from conf import wiki as conf
from Crumbs import Crumbs as crumbs
from locks import Locker

template = open("templates/master.html", "r").read()

class DocHandler (BaseHTTPRequestHandler):
    
    def userisauthorized(self):
        """
            a fast return for authorization status for this user/request. actual auth lookup should
            only be done once
        """
        return True
        
    def wraptemplate(self, **kwargs):
        return re.sub("{{(.*)}}", lambda m: kwargs.get(m.group(1), ""), template)

    def do_GET(self):

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
            
            if path.startswith("/do"):
                # return quickly for adm paths
                self.do_serv(**self.specialhandler(path))
                return

            if path.startswith("/search"):
                self.do_serv(**self.runSearch(path))
                return
                            
            # else, fix up the url a tad    

            if path.startswith("/edit"):
                # we're editing a file. strip "/edit" from the path and flag it
                path = path[5:] 
                editing = True
                action = "Editing"

            # local static files included in this app folder
            if path.startswith("/_static"):
                passthru = True;
                file = "./_static" + path[8:]

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
                    self.do_serv(response=200, body=open(file).read())
                return
            
            if(not os.path.exists(file)):
                out = ".. _" + path[1:] + ":\n\nTitle\n====="
                action = "Creating"
                editing = True
            else: 
                out = read_file(file)

            crumbs = makenavcrumbs(path);
            if(not editing):
                stuff = self.wraptemplate(title = action + " " + path, body = crumbs + parse_data(out), nav = editlink(path))
            else:
                filelock = Locker(file)
                locked = filelock.islocked()
                me = "figgins"
                if locked and not filelock.ownedby(me):
                    stuff = self.wraptemplate(title="File Locked", body = crumbs + "<h3>Can't edit for another " + str(filelock.expiresin()) + " seconds</h3>", nav = rawlink(path))
                else:
                    filelock.lock(me)
                    stuff = self.wraptemplate(title = action + " " + path, body = crumbs + textarea(path, out), nav = rawlink(path)) 
                        
            self.do_serv( body = stuff );
                
        except IOError:
            self.do_serv(response=500, body="oops. internal error.")
    
    def do_POST(self):
        """
            Incoming POST could mean login(?) or save to page. /edit/ has been stripped. It'll always be /login or /a/b/c
        """
        try:
            
            # determine auth, and path.
            #  incoming post data is allegedly replacement for existing .rst of that name
            path = self.path
            if path.startswith("/upload"):
                path = path[7:]
                # this means files in multipart upload need to be put in `path`
                
            else:
                
                file = rstfile(path)
                # ugh. check lock. and owner of the lock.
                filelock = Locker(file)
                locked = filelock.islocked() 
                me = "figgins"
                if not locked or locked and filelock.ownedby(me):
                
                    size = int(self.headers['Content-length'])
                    if(size > 0 and self.userisauthorized()):

                        data = urllib.unquote_plus(self.rfile.read(size)[8:])

                        if not os.path.exists(file):
                            os.makedirs(os.path.dirname(file))
                    
                        print >>open(file, 'w'), data
                        filelock.unlock()

            self.do_GET();
            
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
        args = ["git", cmd, conf['RST_ROOT']];
        #if(cmd == "commit"):
        proc = subprocess.Popen(args, 4096, stdout=subprocess.PIPE);

        return {
            'body': self.wraptemplate(
                body = "<pre>" + proc.communicate()[0] + "</pre>",
                title = "Execution output"
            )
        }
        
    def do_serv(self, **kwargs):
        """
            Sets all headers and serves whatever content it is told to.
        """

        response = kwargs.get("response", 200)
        self.send_response(response)

        if "headers" in kwargs:
            for header in kwargs["headers"]:
                self.send_header(header, headers[header])

        self.end_headers();

        body = kwargs.get("body", "")
        self.wfile.write(body.encode("utf-8"));

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

def parse_data(data):
    overrides = {}
    stuff = core.publish_parts(
        source=data, source_path="/",
        destination_path="/", writer=DojoHTMLWriter(), settings_overrides=overrides)
    return stuff['html_body'];

def editlink(path):
    return "<a href='/edit" + path + "'>edit raw</a> [ <a rel='st' href='#'>status</a> | <a rel='diff' href='#'>diff</a> | <a rel='up' href='#'>update</a> ] "

def rawlink(path):
    # this is kind of useless? add a [cancel] button to the editing form
    return "<a href='" + path + "'>rendered</a>"

def textarea(path, body):
    return "\
        <form method='POST' action='" + path + "'>\
            <div class='resp'><h1>Editing " + path + "</h1><textarea resizeable='true' name='content' style='width:100%; height:400px;'>" + body + "</textarea></div>\
            <button type='submit'>Save</button>\
        </form>"
