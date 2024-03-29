from zope.interface import implements
import zope.interface.verify
from interfaces import IRevisions, IRevision

MODE_PAGE = 0
MODE_USER = 1
MODE_BOTH = 2

class RevisionInitError(Exception):
    pass

class Revisions(object):
    """
    Defines a sequence of revisions for a given entity. Since the MediaWiki API
    does not include a len() method, this class does not provide it either.
    The revision sequence can be queried for revisions between a start and end
    point in either direction, and results will be cached or returned from the
    cache, transparently.

    >>> zope.interface.verify.verifyClass(IRevisions, Revisions)
    True
    """
    # FIXME: Make this a generic cached list class, of which Revisions is a
    # user or subclass.
    implements(IRevisions)
    def __init__(self, site, page=None, user=None):
        self._cache_fragments = {} # Hash(start,end): sequence; auto-merged
        self._site = site
        self._page = page
        self._user = user
        if page and not user:
            self._mode = MODE_PAGE
        elif user and not page:
            self._mode = MODE_USER
        elif user and page:
            self._mode = MODE_BOTH # XXX: May not be implemented
        else:
            raise RevisionInitError("Revisions must be attached to a user or page.")

    def __getitem__(self, revid):
        raise NotImplemented, "Not yet!"

    def __call___(self):
        """
        XXX: Action happens here. Return a generator.
        """
        raise NotImplemented, "Not yet!"

class Revision(object):
    """
    >>> zope.interface.verify.verifyClass(IRevision, Revision)
    True
    """
    implements(IRevision)
    def prev(self):
        raise NotImplemented, "Not yet!"

    def next(self):
        raise NotImplemented, "Not yet!"
