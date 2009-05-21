#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
For a given Wikipedia article, time period and interval periods, this script
calculates a moving average of the number of edits.
"""

import sys
from optparse import OptionParser
import datetime
import csv
import mwclient
from timehelper import parsedate, parseperiod, MWDATEFMT

class NoRevisions(Exception):
    """No revisions found."""


def analyze(article, wiki, start, end, interval, number, output):
    """
    Calculate moving avg of number of edits for the given article and period.
    """
    start = parsedate(start)
    end = parsedate(end)
    interval = parseperiod(interval)

    print "Connecting to %s..." % wiki
    site = mwclient.Site(wiki)
    print "Looking up revisions between %s and %s." % (
        start.strftime(MWDATEFMT), end.strftime(MWDATEFMT))
    sys.stdout.flush()
    page = site.Pages[article]
    if 0: assert isinstance(page, mwclient.page.Page)

    counts = [] # Revision count for each interval. Calculate moving avg later.

    revisions = page.revisions(start=start.strftime(MWDATEFMT),
                               end=end.strftime(MWDATEFMT),
                               dir='newer')
    try:
        rev = revisions.next()
        startid = rev['revid']
    except StopIteration:
        raise NoRevisions

    curdate = start
    revisions = page.revisions(startid=startid,
                               end=end.strftime(MWDATEFMT),
                               dir='newer')
    try:
        counts.append([curdate, 0])
        while True:
            rev = revisions.next()
            revdate = datetime.datetime(*(rev[u'timestamp'][:6]))
            if revdate >= end:
                break
            if revdate >= curdate+interval:
                # New interval.
                print "Revisions for %s - %s: %d" % (
                    curdate.isoformat(), (curdate+interval).isoformat(),
                    counts[-1][1])
                while curdate <= revdate-interval:
                    curdate += interval
                    counts.append([curdate, 0])
            counts[-1][1] += 1
    except StopIteration: # Reached end of revision history
        pass
    # Now calculate moving average
    averages = []
    for counter in range(len(counts) - number + 1):
        averages.append([counts[counter+number-1][0],
                    sum([x[1] for x in counts[counter:counter+number]])/number])
    final = map(lambda c,a: [c[0].strftime('%Y-%m-%d %H:%M:%S'),
                             (c[0]+interval).strftime('%Y-%m-%d %H:%M:%S'),
                             c[1], a[1]],
                counts, [['', '']]*(number-1) + averages)
    final.insert(0, ['Start', 'End', 'Count', 'Average of %d' % number])
    if output:
        print "Saving to %s..." % output
        csv.writer(open(output, 'wb')).writerows(final)
    else:
        import pprint
        pprint.pprint(final)
    # Print Google chart URL for data
    def samples(data, count):
        inc = len(data) / float(count-1)
        pos = 0
        while pos < len(data)-1:
            yield data[int(pos)]
            pos += inc
        yield data[-1]

    chartmax = max([x[1] for x in counts])
    print 'http://chart.apis.google.com/chart' \
          '?chs=600x350' \
          '&chtt=Edits on "%s" between %s and %s' % (article,
                    (start+interval*(number-1)).strftime('%Y-%m-%d'),
                    (end-datetime.timedelta(days=1)).strftime('%Y-%m-%d')) + \
          '&cht=lc' \
          '&chd=t:'+','.join([str(x[2]) for x in final[1+number-1:]]) + '|' + \
                    ','.join([str(x[3]) for x in final[1+number-1:]]) + \
          '&chds=0,' + str(chartmax) + \
          '&chdl=Edit Count|Moving Average' \
          '&chxt=x,y' \
          '&chdlp=t' \
          '&chco=FF8040,4040FF' \
          '&chxl=0:|' + '|'.join([x[0].strftime('%b %-d') for x in samples(counts[number-1:], 12)]) + \
          '&chxr=1,0,' + str(chartmax)


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
    parser.add_option('-i', '--interval', type='string', default='1d',
                      help='Length of each interval [default %default]')
    parser.add_option('-n', '--number', type='int', default=7,
                      help='Number of intervals in moving average [default %default]')
    parser.add_option('-o', '--output', type='string', default=None,
                      help='CSV file to save data to')

    (options, parms) = parser.parse_args(argv)

    if len(parms) < 1:
        print >> sys.stderr, "Article must be specified."
        return 1
    elif len(parms) > 1:
        print >> sys.stderr, "Only one article name may be specified."
        return 1

    return analyze(parms[0], options.wiki, options.start, options.end,
                   options.interval, options.number, options.output)


if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))
