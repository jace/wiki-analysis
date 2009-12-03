from zope.interface import implements
import zope.interface.verify
from interfaces import ISite

import mwclient

from page import Pages
from user import Users


class Site(object):
    """
    Site objects implement a wrapper around the overall MediaWiki API,
    using the mwclient library as a back-end.

    >>> zope.interface.verify.verifyClass(ISite, Site)
    True
    """
    implements(ISite)
    def __init__(self, host, path='/w/', ext='.php', pool=None,
                 retry_timeout=30, max_retries=25):
        self.id = host
        self._mwsite = mwclient.Site(host, path, ext, pool, retry_timeout,
                                     max_retries)
        self.pages = Pages(self) # XXX: Creates circular dependencies
        self.users = Users(self) # XXX: Too. But should be okay.

    def __repr__(self):
        return u'<MediaWiki site %s>' % self.id
