#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
For a given Wikipedia article and time period, this script looks up each
revision and lists the words added and removed, and their word stems.
"""

import sys
from optparse import OptionParser
import datetime
import csv
from nltk.stem.porter import PorterStemmer
import mwclient
from worddiff import worddiff, striptags
from timehelper import parsedate, MWDATEFMT

class NoRevisions(Exception):
    pass

class Stemmer(PorterStemmer):
    def __init__(self, *args, **kw):
        self.cache = {}
        PorterStemmer.__init__(self, *args, **kw)
    
    def stem(self, word):
        if word in self.cache:
            return self.cache[word]
        else:
            self.cache[word] = PorterStemmer.stem(self, word)
            return self.cache[word]


def analyze(article, start, end, wiki, outfile):
    start = parsedate(start)
    end = parsedate(end)

    print "Connecting to %s..." % wiki
    site = mwclient.Site(wiki)
    print "Looking up revisions between %s and %s." % (
        start.strftime(MWDATEFMT), end.strftime(MWDATEFMT))
    if outfile:
        print "Saving table to %s..." % outfile
        out = csv.writer(open(outfile, 'wb'))
        if 0: assert isinstance(out, csv.DictWriter)
        out.writerow(['Timestamp', 'Id', 'User', 'Add/Del'])
    print 'Revisions for "%s":' % article,
    sys.stdout.flush()
    page = site.Pages[article]
    if 0: assert isinstance(page, mwclient.page.Page)

    stem = Stemmer().stem
    revwords = [] # Holds all revisions
    allwords = set()
    revisions = page.revisions(start=start.strftime(MWDATEFMT),
                               end=end.strftime(MWDATEFMT),
                               dir='newer')

    try:
        rev = revisions.next()
        startid = rev['revid']
    except StopIteration:
        raise NoRevisions

    # We have to do this to work around a bug in mwclient.
    revisions = page.revisions(startid=startid,
                               end=end.strftime(MWDATEFMT),
                               dir='newer',
                               prop='ids|timestamp|flags|comment|user|content')

    # This is a typical revision (from the Bangalore page):
    # {u'comment': u'/* Culture and education */',
    #  u'timestamp': (2006, 1, 3, 4, 10, 37, 1, 3, -1),
    #  u'anon': u'', u'revid': 33686266, u'user': u'59.92.138.207'}

    try:
        revision_count = 0
        rev = revisions.next()
        oldcontent = striptags(rev[u'*'])
        while True:
            revstats = {'user': rev[u'user'], 'revid': rev[u'revid'],
                        'timestamp': rev[u'timestamp'],
                        'add': set(), 'del': set(),
                        'addstems': set(), 'delstems': set()}
            print '\rRevisions for "%s": %d on %s' % (article, revision_count,
                '%04d/%02d/%02d %02d:%02d:%02d' % rev[u'timestamp'][:6]),
            sys.stdout.flush()
            rev = revisions.next() # Use first revision only as reference point
            revision_count += 1
            # Analyse content of this edit for words added and removed
            newcontent = striptags(rev[u'*'])
            for change, word in worddiff(oldcontent, newcontent):
                allwords.add(word)
                if change == '+':
                    revstats['add'].add(word.encode('utf-8'))
                    revstats['addstems'].add(stem(word).encode('utf-8'))
                elif change == '-':
                    revstats['del'].add(word.encode('utf-8'))
                    revstats['delstems'].add(stem(word).encode('utf-8'))
            revwords.append(revstats)
            # Done. On to next revision.
            oldcontent = newcontent
            if outfile:
                row = revstats
                rowhead = ['%04d-%02d-%02d %02d:%02d:%02d' %
                                tuple([int(x) for x in row['timestamp'][:6]]),
                           row['revid'], row['user'].encode('utf-8')]
                #print repr(row)
                out.writerow(rowhead + ['Add'] + sorted(row['add']))
                out.writerow(rowhead + ['AddStems'] + sorted(row['addstems']))
                out.writerow(rowhead + ['Del'] + sorted(row['del']))
                out.writerow(rowhead + ['DelStems'] + sorted(row['delstems']))
    except StopIteration:
        pass

    print
    print "Analysed %d revisions with %d words." % (len(revwords), len(allwords))
        
    print "All Done."

def main(argv):
    '''%prog [options] "Article Name"'''
    parser = OptionParser(usage=main.__doc__)
    parser.add_option('-s', '--start',
                      default=(datetime.datetime.utcnow() - datetime.timedelta(weeks=4)).strftime('%Y-%m-%d'),
                      help='Starting date [default %default]')
    parser.add_option('-e', '--end', default='now',
                      help="Ending date (or one of now/today/yesterday) [default %default]")
    parser.add_option('-w', '--wiki', type='string', default='en.wikipedia.org',
                      help='MediaWiki site to look up [default %default]')
    parser.add_option('-o', '--output', type='string', default=None,
                      help='CSV file to save output to')
    (options, parms) = parser.parse_args(argv)

    if len(parms) < 1:
        print >> sys.stderr, "Article must be specified."
        return 1
    elif len(parms) > 1:
        print >> sys.stderr, "Only one article name may be specified."
        return 1

    return analyze(parms[0], options.start, options.end, options.wiki,
                   options.output)


if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))
