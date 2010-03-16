#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
For a given Wikipedia article and time period, this script looks up all
the editors involved and all the other articles they have worked on, and prints
an "editor,article" list.
"""

import sys
from optparse import OptionParser
import datetime
import csv
import mwclient
from timehelper import parsedate, MWDATEFMT

class IgnoreEditor(Exception):
    pass

def analyze(article, start, end, wiki, ignore, outfile, filtercount,
            filterminedits, filtermaxedits, nefile, nafile):
    start = parsedate(start)
    end = parsedate(end)
    print "Start date:", start
    print "End date:", end
    print "Connecting to %s..." % wiki
    site = mwclient.Site(wiki)
    print 'Revisions for "%s":' % article,
    page = site.Pages[article]
    if 0: assert isinstance(page, mwclient.page.Page)

    # Place all editors in a dictionary
    editors = {}
    revisions = page.revisions(start=start.strftime(MWDATEFMT),
                               end=end.strftime(MWDATEFMT),
                               dir='newer')
    try:
        rev = revisions.next()
        startid = rev['revid']
    except StopIteration:
        raise NoRevisions

    # We have to do this to work around a (now fixed?) bug in mwclient.
    revisions = page.revisions(startid=startid,
                               end=end.strftime(MWDATEFMT),
                               dir='newer')

    # This is a typical revision (from the Bangalore page):
    # {u'comment': u'/* Culture and education */',
    #  u'timestamp': (2006, 1, 3, 4, 10, 37, 1, 3, -1),
    #  u'anon': u'', u'revid': 33686266, u'user': u'59.92.138.207'}

    try:
        revision_count = 0
        bots = set()
        rev = revisions.next()
        while datetime.datetime(*rev[u'timestamp'][:6]) <= end: # Within daterange?
            revision_count += 1
            print '\rRevisions for "%s": %d until %s' % (article, revision_count,
                '%04d/%02d/%02d %02d:%02d:%02d' % rev[u'timestamp'][:6]),
            # Make dictionary keys of editor names, but don't assign values yet
            # Ignore editors we've been asked to. Ignore bots automatically.
            if rev[u'user'] not in ignore and rev[u'user'] not in bots:
                userinfo = site.users([rev[u'user']]).next()
                if 'bot' in userinfo.get('groups', []):
                    print "Skipping bot %s" % rev[u'user']
                    bots.add(rev[u'user'])
                else:
                    editors[rev[u'user']] = None
            rev = revisions.next()
    except StopIteration:
        pass

    print

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
            contribs = site.usercontributions(editor,
                                              start=start.strftime(MWDATEFMT),
                                              end=end.strftime(MWDATEFMT),
                                              dir='newer')
            #startid = contribs.next()['revid']
            ## The same (fixed) mwclient bug again:
            #contribs = site.usercontributions(editor,
            #                                  startid=startid,
            #                                  end=end.strftime(MWDATEFMT),
            #                                  dir='newer')
            print "Pages for %s: ..." % editor.encode('utf-8'),
            rev = contribs.next()
            page_count = 0
            while datetime.datetime(*rev[u'timestamp'][:6]) <= end:
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

        except KeyboardInterrupt:
            # Skip an editor if user is getting impatient
            del editors[editor]
            ignored_editors.append(editor)
        except StopIteration:
            # This shouldn't happen unless something is wrong
            del editors[editor]
            ignored_editors.append(editor)
        except IgnoreEditor:
            print "\rPages for %s: ignoring editor since"\
                  " page count %d is out of range %d-%d." % (
                      editor.encode('utf-8'), len(lpages),
                      filterminedits, filtermaxedits)
            del editors[editor]
            ignored_editors.append(editor)

    editor_names = editors.keys() # Re-assign in case someone got dropped
    editor_names.sort()
    page_names = pages.keys()
    page_names.sort()

    print
    print "Ignored editors: %s" % u', '.join(ignored_editors).encode('utf-8')

    if outfile:
        useids = False
        if nefile and nafile:
            useids = True
            # Substitute editor and article names with id numbers
            ideditors = {}
            idarticles = {}

            for counter in range(len(editor_names)):
                ideditors[editor_names[counter].encode('utf-8')] = counter
            for counter in range(len(page_names)):
                idarticles[page_names[counter].encode('utf-8')] = counter

            csv.writer(open(nefile, 'wb')).writerows([x[::-1] for x in ideditors.items()])
            csv.writer(open(nafile, 'wb')).writerows([x[::-1] for x in idarticles.items()])

        print "Saving table to %s..." % outfile
        out = csv.writer(open(outfile, 'wb'))
        if 0: assert isinstance(out, csv.DictWriter)
        for editor in editors:
            for article in editors[editor].keys():
                if useids:
                    out.writerow([ideditors[editor.encode('utf-8')], idarticles[article.encode('utf-8')]])
                else:
                    out.writerow([editor.encode('utf-8'), article.encode('utf-8')])

        print "Total articles: %d" % len(pages)


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
                      help='CSV file to save the editor and article list to')
    parser.add_option('--ne', type='string', default=None,
                      help='CSV file to save editor id numbers to')
    parser.add_option('--na', type='string', default=None,
                      help='CSV file to save article id numbers to')
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

    return analyze(parms[0], options.start, options.end, options.wiki,
                   options.ignore, options.output, options.filterpages,
                   options.filterminedits, options.filtermaxedits,
                   options.ne, options.na)


if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))
