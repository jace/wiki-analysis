#!/usr/bin/env python
import sys
import csv
from itertools import imap
from pprint import pprint
import pygooglechart


def run(datasource):
    # Figure out data positions from header labels.
    headers = datasource.next()
    edit_pos = editor_pos = start_pos = None
    for pos, header in enumerate([s.lower() for s in headers]):
        if header.startswith('sum of '):
            edit_pos = pos
        elif header == 'editors in window':
            editor_pos = pos
        elif header == 'start':
            date_pos = pos
    if edit_pos is None or editor_pos is None:
        raise ValueError, "Missing required headers in data file."

    data = []
    chartdata = []
    scale = 0
    for row in datasource:
        date = row[date_pos]
        editors = row[editor_pos]
        edits = row[edit_pos]
        if editors == '' or edits == '':
            # First few rows, before window starts
            continue
        data.append([date, editors, edits])

        a = float(editors)
        b = float(edits)
        x = a
        if a == 0:
            y = 0
        else:
            y = (a**(1+a/b))/b
        chartdata.append([date, x, y])
        scale = max([scale, int(x), int(y)])

    # We have chart data. Let's plot it.
    chart = pygooglechart.ScatterChart(600, 300)#, x_range = (0, scale),
                                       #y_range = (0, scale))
    chart.add_data([r[1] for r in chartdata]) # x
    chart.add_data([r[2] for r in chartdata]) # y
    print chart.get_url()
    return chartdata


def main(argv):
    if len(argv) not in [2, 3]:
        print >> sys.stderr, "Syntax: %0 data.csv [output.csv]"
    filename = argv[1]
    if len(argv) == 3:
        outfile = argv[2]
    else:
        outfile = None
    data = run(csv.reader(open(filename, 'rb')))
    if outfile:
        csv.writer(open(outfile, 'wb')).writerows(data)


if __name__=='__main__':
    sys.exit(main(sys.argv))