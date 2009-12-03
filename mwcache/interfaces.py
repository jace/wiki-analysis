from zope.interface import Interface
from zope.schema import Int, Text, Bool, Object, Datetime, Dict, List


class IPages(Interface):
    """
    Container for all pages in a Site.
    """

    def __getitem___(self, page):
        """Returns an IPage object for the specified page."""


class IUsers(Interface):
    """
    Collection of users on the site.
    """
    def __getitem___(self, user):
        """Returns an IUser object for the specified user."""

    def cache(self, usernames):
        """Get multiple users into the cache."""


class ISite(Interface):
    """
    Defines a MediaWiki site.
    """
    id = Text()
    pages = Object(IPages)
    users = Object(IUsers)


class IRevisions(Interface):
    """
    Defines a stream of revisions for a given page or user. Caches data
    and retrieves from upstream to fill gaps in the cache. An IRevision's
    length is undefined because
    """
    def __getitem__(self, number):
        """Returns an IRevision object for the given sequence number."""
    def get(self, revisionid):
        """Returns an IRevision object for the given revision id."""


class IPage(Interface):
    """
    Defines a page on a site.
    """
    revisions = Object(IRevisions)


class IUser(Interface):
    """
    Defines a user on the MediaWiki site. Users make revisions to pages.
    """
    id = Text(readonly=True)
    refreshed = Datetime() # Date when info was last refreshed
    contribs = Object(IRevisions)
    blockinfo = Dict()
    groups = List()
    editcount = Int()
    registration = Datetime()
    emailable = Bool()


class IRevision(Interface):
    """
    Defines a single revision from the MediaWiki site. Revisions are attached
    to two primary revision streams, for the page and for the user.
    """
    id = Int(readonly=True)
    parentid = Int(required=False)
    minor = Bool()
    anon = Bool()
    user = Object(IUser)
    page = Object(IPage)
    text = Text(required=False)
