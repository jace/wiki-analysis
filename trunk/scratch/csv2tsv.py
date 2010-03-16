#!/usr/bin/env python

import sys
import csv

if len(sys.argv) != 3:
    print >> sys.stderr, "Usage: %s input.csv output.txt" % sys.argv[0]
    sys.exit(1)

infile, outfile = sys.argv[1:]
if outfile == '-':
    outfile = sys.stdout
else:
    outfile = open(outfile, 'w')

for row in csv.reader(open(infile, 'rb')):
    print >> outfile, '\t'.join(row)
