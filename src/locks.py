#!/usr/bin/env python
# encoding: utf-8
"""
locks.py
"""

import os, time

class Locker(object):
    
    # number of seconds to allow a lock to exist
    expiretime = 5 * 60 

    def _lockfile_exists(self):
        return os.path.exists(self.lockfile)

    def _times(self):
        self.filetime = int(os.stat(self.lockfile).st_mtime)
        self.age = int(time.time()) - self.filetime

    def expiresin(self):
        """
            Return time in seconds that this file will expire
        """
        if self._isexpired(): return 0
        else: return self.expiretime - self.age

    def _isexpired(self):
        self._times()
        return self.age >= self.expiretime

    def unlock(self):
        if self._lockfile_exists():
            os.remove(self.lockfile)

    def lock(self, owner):
        if self.exists and not self.islocked():
            print >>open(self.lockfile, 'w'), owner    
        return self

    def islocked(self):
        if self._lockfile_exists():
            if self._isexpired():
                self.unlock()
                return False
            return True
        else:
            return False

    def owner(self):
        if self._lockfile_exists():
            return open(self.lockfile, 'r').read().strip()
        
    def ownedby(self, name):
        if self._lockfile_exists():
            return self.owner() == name.strip()
        else:
            return False

    def __init__(self, path):
        self.file = path
        self.lockfile = self.file + "_lock"
        self.exists = os.path.exists(self.file)
