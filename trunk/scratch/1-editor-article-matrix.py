#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
For a given Wikipedia article and time period. this script looks up all
the editors involved and all the other articles they have worked on.
"""

import sys
from optparse import OptionParser
import datetime
import csv
import mwclient

class IgnoreEditor(Exception):
    pass

def analyze(article, days, wiki, ignore, outfile, filtercount,
            filterminedits, filtermaxedits):
    until = datetime.datetime.now() - datetime.timedelta(days=days)
    print "Connecting to %s..." % wiki
    site = mwclient.Site(wiki)
    print 'Looking up article "%s"...' % article
    page = site.Pages[article]
    if 0: assert isinstance(page, mwclient.page.Page)

    # Place all editors in a dictionary
    editors = {}
    revisions = page.revisions()

    # This is a typical revision (from the Bangalore page):
    # {u'comment': u'/* Culture and education */',
    #  u'timestamp': (2006, 1, 3, 4, 10, 37, 1, 3, -1),
    #  u'anon': u'', u'revid': 33686266, u'user': u'59.92.138.207'}

    try:
        rev = revisions.next()
        while datetime.datetime(*rev[u'timestamp'][:6]) >= until: # Within daterange?
            # Make dictionary keys of editor names, but don't assign values yet
            # Ignore editors we've been asked to
            if rev[u'user'] not in ignore:
                editors[rev[u'user']] = None
                rev = revisions.next()
    except StopIteration:
        pass

    editor_names = editors.keys()
    editor_names.sort() # Will make table generation easier further down
    print "Found %d editors:" % len(editor_names),
    print u', '.join(editor_names).encode('utf-8')

    # pages[page_title] = [list_of_editors]
    pages = {} # Pages across all editors
    ignored_editors = []

    for editor in editor_names:
        try:
            lpages = {} # Pages for this editor
            contribs = site.usercontributions(editor)
            print "Pages for %s: ..." % editor.encode('utf-8'),
            rev = contribs.next() # No try/except since they have at least one edit
            page_count = 0
            while datetime.datetime(*rev[u'timestamp'][:6]) >= until:
                if rev[u'title'] not in lpages:
                    page_count += 1
                    print "\rPages for %s: %d..." % (editor.encode('utf-8'),
                                                     page_count),
                    sys.stdout.flush()
                    if filtermaxedits != 0 and page_count > filtermaxedits:
                        # This editor has edited too many pages. Ignore them
                        raise IgnoreEditor
                    # Keep track of number of edits for each page
                    lpages[rev[u'title']] = 1
                else:
                    lpages[rev[u'title']] = lpages[rev[u'title']] + 1

                try:
                    rev = contribs.next()
                except StopIteration:
                    break
            if filterminedits != 0 and len(lpages) < filterminedits:
                raise IgnoreEditor
            editors[editor] = lpages
            #editors[editor].sort()
            print "\rPages for %s:" % editor.encode('utf-8'),
            lpage_names = lpages.keys()
            lpage_names.sort()
            if len(lpages) > 10:
                print u', '.join(['%s [%d]' % (p, lpages[p]) for p in lpage_names[:10]]).encode('utf-8'),
                print "... (%d total)" % len(lpages)
            else:
                print u', '.join(['%s [%d]' % (p, lpages[p]) for p in lpage_names]).encode('utf-8')

            for item in lpage_names:
                page_editors = pages.get(item, [])
                page_editors.append(editor)
                pages[item] = page_editors

        except IgnoreEditor:
            print "\rPages for %s: ignoring editor since"\
                  " page count %d is out of range %d-%d." % (
                      editor.encode('utf-8'), len(lpages),
                      filterminedits, filtermaxedits)
            del editors[editor]
            ignored_editors.append(editor)

    editor_names = editors.keys() # Re-assign in case someone got dropped
    editor_names.sort()

    print
    print "Ignored editors: %s" % u', '.join(ignored_editors).encode('utf-8')

    if outfile:
        print "Saving table to %s..." % outfile
        out = csv.writer(open(outfile, 'wb'))
        if 0: assert isinstance(out, csv.DictWriter)
        out.writerow(['Article/Editor'] + [e.encode('utf-8') for e in editor_names])
        out.writerow(['Page Counts'] + [len(editors[e]) for e in editor_names])
        page_names = pages.keys()
        page_names.sort()
        print "Total articles: %d" % len(page_names)
        save_count = 0
        for p in page_names:
            page_editors = pages[p]
            row = [editors[e][p] if e in page_editors else 0 for e in editor_names]
            if sum(row) >= filtercount:
                out.writerow([p.encode('utf-8')]+row)
                save_count += 1
        print "Saved articles: %d" % save_count

def main(argv):
    '''%prog [options] "Article Name"'''
    parser = OptionParser(usage=main.__doc__)
    parser.add_option('-d', '--days', type='int', default=30,
                      help='Number of days of revision history to look up'\
                      ' [default %default]')
    parser.add_option('-w', '--wiki', type='string', default='en.wikipedia.org',
                      help='MediaWiki site to look up [default %default]')
    parser.add_option('-i', '--ignore', type='string', action='append', default=[],
                      help='Ignore edits by this editor'\
                      ' (useful to filter maintenance bots)')
    parser.add_option('-o', '--output', type='string', default=None,
                      help='CSV file to save the article/editor matrix to')
    parser.add_option('-p', '--filterpages', type=int, default=2, dest='filterpages',
                      help='Filter pages without at least so many editors'\
                      ' [default %default]')
    parser.add_option('-f', '--filterminedits', type=int, default=0,
                      help='Filter editors with less than specified edits'\
                      ' (useful to ignore one-off editors, default no lower limit)')
    parser.add_option('-F', '--filtermaxedits', type=int, default=0,
                      help='Filter editors with more than specified edits'\
                      ' (useful to ignore admins who edit all over)')
    (options, parms) = parser.parse_args(argv)

    if len(parms) < 1:
        print >> sys.stderr, "Article must be specified."
        return 1
    elif len(parms) > 1:
        print >> sys.stderr, "Only one article name may be specified."
        return 1

    return analyze(parms[0], options.days, options.wiki, options.ignore,
                   options.output, options.filterpages,
                   options.filterminedits, options.filtermaxedits)


if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))
