#!/usr/bin/env python
# -*- coding: utf-8  -*-

import sys
import re

def makeSentences(text):
    rawlist = text.split('.')
    return [line.strip() for line in rawlist]

def run(word, oldtext, newtext):
    old = makeSentences(oldtext)
    new = makeSentences(newtext)

def main(argv):
    if len(sys.argv) != 4:
        print "Syntax: word-sentences.py word old.txt new.txt"
    else:
        word, file1, file2 = argv[1:]
        file1data = open(file1, 'rb').read().replace('\r\n', '\n').replace('\n', ' ')
        file2data = open(file2, 'rb').read().replace('\r\n', '\n').replace('\n', ' ')
        return run(word, file1data, file2data)

if __name__=='__main__':
    if '-t' in sys.argv:
        import doctest
        doctest.testmod()
    else:
        sys.exit(main(sys.argv))
