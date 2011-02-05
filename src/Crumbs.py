#!/usr/bin/env python
# encoding: utf-8
"""
Crumbs.py

Created by Peter Higgins on 2011-02-04.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

class Crumbs(object):
    """
        Simple breadcrumb making thing, with special consideration for root/index and a/b/c-d (parent is a/b/c, not a/b)
        Actually that second part is a lie. But it should happen.
    """
    
    def __init__(self, url):
        self.crumbs = []
        for crumb in url.split('/'):
            if crumb.find("-") > -1:
                parts = crumb.split("-")
                self.crumbs.append(parts[0])
            self.crumbs.append(crumb)
    
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
