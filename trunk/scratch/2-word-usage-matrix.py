#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
For a given Wikipedia article and time period, this script looks up all
the changes introduced by each editor and tallies what words they used or
removed.
"""

# TODO:
# 1. Accept start/end date ranges. Parse strings in the yyyy-mm-dd format.
# 2. Test mwclient's start/end specification for revisions.
# 3. Ask mwclient to get full content of pages and in old-to-new sequence.
# 4. Keep track of previous revision content.
# 5. Remove code related to other pages by the same editor.
# 6. Perform a diff to get exact words added or removed. Tricky bit.
# 7. Sort words and use counts (number added, number removed, separately!)
# 8. Save to CSV(s).

import sys
from optparse import OptionParser
import datetime
import csv
import mwclient
from worddiff import worddiff, striptags
from timehelper import parsedate, MWDATEFMT

class IgnoreEditor(Exception):
    pass

def analyze(article, start, end, wiki, ignore, outfile):
    start = parsedate(start)
    end = parsedate(end)

    print "Connecting to %s..." % wiki
    site = mwclient.Site(wiki)
    print "Looking up revisions between %s and %s." % (
        start.strftime(MWDATEFMT), end.strftime(MWDATEFMT))
    print 'Revisions for "%s":' % article,
    sys.stdout.flush()
    page = site.Pages[article]
    if 0: assert isinstance(page, mwclient.page.Page)

    # Place all editors in a dictionary
    editors = {} # Dictionary of word: (add count, remove count)
    edit_counts = {}
    allwords = set() # Set of all words found across editors

    revisions = page.revisions(start=start.strftime(MWDATEFMT),
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
            print '\rRevisions for "%s": %d on %s' % (article, revision_count,
                '%04d/%02d/%02d %02d:%02d:%02d' % rev[u'timestamp'][:6]),
            sys.stdout.flush()
            rev = revisions.next() # Use first revision only as reference point
            revision_count += 1
            # Ignore editors we've been asked to
            if rev[u'user'] not in ignore:
                edit_counts[rev[u'user']] = edit_counts.get(rev[u'user'], 0) + 1
                editorstats = editors.get(rev[u'user'], {})
                # Analyse content of this edit for words added and removed
                newcontent = striptags(rev[u'*'])
                for change, word in worddiff(oldcontent, newcontent):
                    allwords.add(word)
                    wordstats = editorstats.get(word, (0, 0))
                    if change == '+':
                        editorstats[word] = (wordstats[0] + 1, wordstats[1])
                    elif change == '-':
                        editorstats[word] = (wordstats[0], wordstats[1] + 1)
                editors[rev[u'user']] = editorstats
            # Done. On to next revision.
            oldcontent = newcontent
    except StopIteration:
        pass

    print

    editor_names = editors.keys()
    editor_names.sort() # Will make table generation easier further down
    print "Found %d editors with %d words: %s" % (len(editor_names), len(allwords),
        u', '.join(editor_names).encode('utf-8'))

    if outfile:
        print "Saving table to %s..." % outfile
        out = csv.writer(open(outfile, 'wb'))
        if 0: assert isinstance(out, csv.DictWriter)
        out.writerow(['Word/Editor'] + [e.encode('utf-8') for e in editor_names])
        out.writerow(['Edit Count'] + [edit_counts[e] for e in editor_names])
        sorted_words = list(allwords)
        sorted_words.sort()
        for word in sorted_words:
            row = [editors[e].get(word, (0,0)) for e in editor_names]
            out.writerow([word.encode('utf-8')]+row)
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
    parser.add_option('-i', '--ignore', type='string', action='append', default=[],
                      help='Ignore edits by this editor'\
                      ' (useful to filter maintenance bots)')
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
                   options.ignore, options.output)


if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))
