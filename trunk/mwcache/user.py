from zope.interface import implements
from interfaces import ISite

from datetime import datetime
from utils import mwdatetime


class UserMissing(Exception):
    """Unknown user"""
    pass


class UserAmbiguous(Exception):
    """Ambiguous username"""
    pass


class Users(object):
    """
    Container for all users on the site. Case sensitive. Current versions of
    MediaWiki require the name to start with an uppercase character.
    """
    def __init__(self, site):
        self._site = site
        self._cache = {}

    def __repr__(self):
        return u'<Users on %s>' % self._site.id

    def __getitem__(self, username):
        if username in self._cache:
            return self._cache[username]
        else:
            user = User(self._site, username)
            self._cache[username] = user
            return user

    def cache(self, usernames):
        """Get multiple users into the cache."""
        getusers = set()
        for username in usernames:
            if username not in self._cache:
                getusers.add(username)
        results = self._site._mwsite.users(getusers,
            prop='blockinfo|groups|editcount|registration|emailable')
        for userdata in results:
            username = userdata['name']
            try:
                self._cache[username] = User(self._site, username, userdata)
            except UserMissing:
                pass


class User(object):
    """
    Defines a user on the site.
    """
    def __init__(self, site, username, data={}):
        self._site = site
        self.id = username
        self.refresh(updateid=True, data=data)

    def __repr__(self):
        return u'<User %s on %s>' % (self.id, self._site.id)

    def refresh(self, updateid=False, data={}):
        username = self.id
        if not data:
            data = self._site._mwsite.users([username],
                prop='blockinfo|groups|editcount|registration|emailable').next()
        if 'missing' in data or data.get('registration', None) is None:
            raise UserMissing(username)
        if data['name'] != username:
            raise UserAmbiguous(username)
        if updateid:
            self.id = data['name']

        self.refreshed = datetime.now()
        self.editcount = data['editcount']
        self.registration = mwdatetime(data['registration'])
        self.emailable = True if 'emailable' in data else False
