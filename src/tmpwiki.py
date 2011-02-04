"""
    the original server. Steal as needed. do_get() logic is sound. 
"""

from docutils import nodes, utils
from docutils import core, io
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys, os, re
import urllib
import subprocess, codecs

def rstfile(path):
    return "../_source-moin" + path + ".rst"
    
# replace with a proper html template. we only care about text being in the body.
def wrap(title, text, nav):
    return "\
    <!doctype html>\
        <html>\
        <head>\
            <link rel='stylesheet' href='/_static/js/docs/wiki.css'>\
            <title>" + title + "</title>\
        </head>\
        <body class='claro'>\
            <div id='nav'><div class='wrap'>" + nav + "</div></div><div class='wrap'>" + text + "</div>\
            <script src='/_static/js/dojo/dojo.js'></script>\
            <script src='/_static/js/docs/wiki.js'></script>\
        </body>\
    </html>"

def makenav(old, path):
    # determine auth, show login or edit nav?
    return old
    
def makenavcrumbs(old, path):
    if(path.startswith("/")):
        path = path[1:]
    parts = Crumbs(path);
    return "<div class='crumbs'><a href='/'>home</a> / " + " / ".join(parts.links()) + "</div>"

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

# simple server:
class DocHandler (BaseHTTPRequestHandler):
    
    def runSearch(self, path):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers();
        term = path[1:].split("/")[1]
        print "searching: ", term
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
        
        out = "<html><head></head><body><div><h2>Results for: " + term + "</h2><ul>" + "\n".join(tout) +  "</ul></div></body></html>"
        self.wfile.write(out)
    
    def specialhandler(self, path):
        self.send_response(200)
        self.end_headers();
        cmd = path[1:].split("/")[1]
        args = ["svn", cmd, "../_source-moin"];
        #if(cmd == "commit"):
            
        proc = subprocess.Popen(args, 4096, stdout=subprocess.PIPE);
        self.wfile.write(proc.communicate()[0])
    
    def do_GET(self):
        try:
            
            # static files should never be served from here. this is just a router for non
            # static files. path will be something like one of the following:
            #
            # /                 becomes /index
            # /dojo             becomes /dojo/index
            # /dojo/index       becomes /dojo/index
            # /edit/dojo/       becomes /edit/dojo/index
            # /edit/dojo/index  becomes /edit/dojo/index
            # /edit/index       becomes /edit/index
            # /edit/            becomes /edit/index
            # /dojo/byId        becomes /dojo/byId
            # /dijit/form/Form  becomes /dijit/form/Form
            # /adm/*            becomes /adm/*
            # /_static/         should be served by proxy, shared with ref-guide _static
            # /*.jpg            images attached to wiki
            # /my/              becomes ./site/ (pseudo local files for dev at this time)
            
            path = self.path
            editing = False
            passthru = False
            action = ""
            
            if path.startswith("/adm"):
                # return quickly for adm paths
                self.specialhandler(path)
                return

            if path.startswith("/search"):
                self.runSearch(path);
                return
                            
            # fix up the url a tad    

            if path.startswith("/edit"):
                # we're editing a file. strip "/edit" from the path and flag it
                path = path[5:] 
                editing = True
                action = "Editing"

            # local static files included in this app folder
            if path.startswith("/my"):
                passthru = True;
                file = "./site" + path[3:]

            # if we're the root, always add `index`
            if path == "/" or path.endswith("/"): path += "index"
            parts = path.split("/")
            
            # files in the root need to be += index (djConfig, others in root don't follow this :/)
            # if len(parts) == 2 and parts[1] != "site.css":
            #    path += "/index";

            # wiki referenced image handling. all are in source tree:
            # note, static url's won't make it this far by way of ProxyPass from apache
            if path.endswith("jpg") or path.endswith("png") or path.endswith("gif"):
                file = "../_source-moin" + path
                passthru = True
            elif not passthru:
                file = rstfile(path)
                        
            if(passthru):
                # direct LINK
                self.send_response(200)
                self.end_headers();
                self.wfile.write(open(file).read())
                return
            
            if(not os.path.exists(file)):
                out = ".. _" + path[1:] + ":\n\nTitle\n====="
                action = "Creating"
                editing = True
            else: 
                out = read_file(file)
                                        
            self.send_response(200);
            self.send_header('Content-type', 'text/html')
            self.end_headers();
            
            crumbs = makenavcrumbs('', path);
            if(not editing):
                stuff = wrap(action + " " + path, crumbs + parse_data(out), makenav(editlink(path), path))
            else:
                stuff = wrap(action + " " + path, crumbs + textarea(path, out), rawlink(path)) 
            
            self.wfile.write(stuff.encode("utf-8"));
                
        except IOError:
            self.send_response(404)
    
    def do_POST(self):
        
        try:
            
            # determine auth, and path.
            #  incoming post data is allegedly replacement for existing .rst of that name
            file = rstfile(self.path)
            size = int(self.headers['Content-length'])
            if(size > 0 and userisauthorized(self)):

                if(os.path.exists(file)):
                    data = urllib.unquote_plus(self.rfile.read(size)[8:])
                    print >>open(file, 'w'), data
                else:
                    print "Wanted to save " + file + "but not found."
                    # else we need to create it too? (svn add ...)

            self.do_GET();
            
        except IOError:
            self.send_response(500)

def userisauthorized(http):
    # put LDAP checkage here maybe?
    return True
    
# read out parsed rst from some filename
def read_file(filename):
    if(os.path.exists(filename)):
        f = codecs.open(filename, "r", "utf-8")
        # f = open(filename)
        data = f.read()
        return data;

from directives import DojoHTMLWriter
def parse_data(data):
    overrides = {}
    stuff = core.publish_parts(
        source=data, source_path="/",
        destination_path="/", writer=DojoHTMLWriter(), settings_overrides=overrides)
    return stuff['html_body'];

class Crumbs(object):
    def __init__(self, url):
        self.crumbs = url.split('/')
    
    def links(self):
        self.list = []
        count = 0
        for crumb in self.crumbs:
            str = ""
            exstr = ""
            if count == 0 and crumb != "index": 
                exstr = "/index"
            else: 
                exstr = ""
            for c in range(count + 1):
                str += '/' + self.crumbs[c]
            count += 1
            self.list.append('<a href="' + str + exstr + '">' + crumb + '</a>');

        return self.list

# looooooop
def main():
    try:
        server = HTTPServer(('', 4200), DocHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
        
if __name__ == '__main__':
    main()
