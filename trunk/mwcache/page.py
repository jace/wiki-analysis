from zope.interface import implements
from interfaces import ISite

from revision import Revisions

class PageMissing(Exception):
    """Unknown page"""
    pass


class Pages(object):
    """
    Container for pages on site.
    """
    def __init__(self, site):
        self._site = site
        self._cache = {}

    def __getitem__(self, pagename):
        if pagename in self._cache:
            return self._cache[pagename]
        else:
            page = Page(self._site, pagename)
            self._cache[pagename] = page
            return page


class Page(object):
    """
    Represents a page on the site. Pages contain revisions.
    """
    def __init__(self, site, pagename):
        self._site = site
        self.id = pagename
        self.revisions = Revisions(site, page=self)
