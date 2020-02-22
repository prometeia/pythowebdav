#Copyright (c) 1999 Christian Scholz (ruebe@aachen.heimat.de)
#
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Library General Public
#License as published by the Free Software Foundation; either
#version 2 of the License, or (at your option) any later version.
#
#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#Library General Public License for more details.
#
#You should have received a copy of the GNU Library General Public
#License along with this library; if not, write to the Free
#Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
#MA 02111-1307, USA

"""
Python WebDAV Server.

This is an example implementation of a DAVserver using the DAV package.

"""

import logging
import warnings
from pywebdav.lib.WebDAVServer import DAVRequestHandler


log = logging.getLogger()

class DAVAuthHandler(DAVRequestHandler):
    """
    Provides authentication based on parameters. The calling
    class has to inject password and username into this.
    (Variables: auth_user and auth_pass)
    """

    # Do not forget to set IFACE_CLASS by caller
    # ex.: IFACE_CLASS = FilesystemHandler('/tmp', 'http://localhost/')
    _config = None

    @property
    def verbose(self):
        return self._config.DAV.verbose

    @property
    def DO_AUTH(self):
        return not self._config.DAV.noauth

    @classmethod
    def inject_config(cls, config):
        if cls._config is not None:
            warnings.warn("Configuration already injected")
        cls._config = config

    def _log(self, message):
        if self.verbose:
            log.info(message)

    def get_userinfo(self, user, pw, command):
        """ authenticate user """
        if not self._config.DAV.user or not  self._config.DAV.password:
            log.error("Empty master user/password, cannot authenticate")
            return
        if user == self._config.DAV.user and pw == self._config.DAV.password:
            log.info('Successfully authenticated user %s' % user)
            return True
        log.info('Authentication failed for user %s' % user)
        return False

