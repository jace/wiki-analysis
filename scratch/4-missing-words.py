#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
For a given Wikipedia article and number of days of history, this script looks
up all the changes introduced by each editor and finds all the words that are
no longer on the current revision of the page.

This is a demo for FOSS.in 2009.
"""

# Process:
# 1. Take number of days
# 2. Get most recent revision. Wordify it. Make set of words
# 3. Make empty set for historical words
# 4. Get earlier revision, wordify it, add to set
# 5. Break when done with history
# 6. Subtract current words from historical words. Display


import sys
from optparse import OptionParser
import datetime
import mwclient
from worddiff import getwords, striptags
from timehelper import MWDATEFMT, parseperiod


class NoRevisions(Exception):
    pass


def analyze(article, days, wiki):
    days = parseperiod(days)
    end = datetime.datetime.now() - days

    print "Connecting to %s..." % wiki
    site = mwclient.Site(wiki)
    print "Looking up revisions back to %s." % (end.strftime(MWDATEFMT))
    print 'Revisions for "%s":' % article,
    sys.stdout.flush()
    page = site.Pages[article]
    if 0: assert isinstance(page, mwclient.page.Page)

    allwords = set() # Set of all words found across editors

    revisions = page.revisions(end=end.strftime(MWDATEFMT),
                               prop='ids|timestamp|flags|comment|user|content')

    try:
        rev = revisions.next()
        content = striptags(rev[u'*'])
        currentwords = set(getwords(content)) # Words in current revision
    except StopIteration:
        raise NoRevisions

    # This is a typical revision:
    # {u'comment': u'/* Culture and education */',
    #  u'timestamp': (2006, 1, 3, 4, 10, 37, 1, 3, -1),
    #  u'anon': u'', u'revid': 33686266, u'user': u'59.92.138.207'}

    try:
        revision_count = 0
        while True:
            print '\rRevisions for "%s": %d on %s' % (article, revision_count,
                '%04d/%02d/%02d %02d:%02d:%02d' % rev[u'timestamp'][:6]),
            sys.stdout.flush()
            rev = revisions.next() # Use first revision only as reference point
            revision_count += 1
            # Analyse content of this edit for words added and removed
            content = striptags(rev[u'*'])
            allwords.update(set(getwords(content)))
            # Done. On to next revision.
    except StopIteration:
        pass

    print

    print "Words in the revision history that are not in the current revision:"

    print ', '.join([word.encode('utf-8') for word in (allwords - currentwords)])


def main(argv):
    '''%prog [options] "Article Name"'''
    parser = OptionParser(usage=main.__doc__)
    parser.add_option('-d', '--days', default='30d',
                      help="Days of history to look up [default %default]")
    parser.add_option('-w', '--wiki', type='string', default='en.wikipedia.org',
                      help='MediaWiki site to look up [default %default]')
    (options, parms) = parser.parse_args(argv)

    if len(parms) < 1:
        print >> sys.stderr, "Article must be specified."
        return 1
    elif len(parms) > 1:
        print >> sys.stderr, "Only one article name may be specified."
        return 1

    return analyze(parms[0], options.days, options.wiki)


if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))
