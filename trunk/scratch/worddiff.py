#/usr/bin/env python
# -*- coding: utf-8  -*-

"""
Word Differ
===========

Returns words that have been added or removed between two pieces of text.
"""

__author__ = 'Kiran Jonnalagadda <jace@pobox.com>'

import re
import difflib

# Ignore common punctuation but notably not apostropes, straight or curved.
IGNORECHARS=u' \t,./<>?[]{}\\|`~!@#$%^&*()-_=+;:"\r\n'\
            u'«»¡¿¢£¤¥¦§¬¶·×÷         ​‌‐‑‒–—―‘‚‛“”„‟‹›‼‽‾'

def _makecharregex(chars):
    result = chars.replace('\\', '\\\\').replace(
        '[', '\\[').replace(']', '\\]').replace('.', '\\.').replace(
        '?', '\\?').replace('*', '\\*').replace('-', '\\-').replace(
        '^', '\\^')
    result = '[' + result + ']+'
    return result

resplit = re.compile(_makecharregex(IGNORECHARS))
resplit = re.compile('\W+') # XXX: Apostrophe eating splitter
resplitsentence = re.compile('[\.?!|]+')
retag = re.compile('<.*?>')

def striptags(text):
    """
    Remove HTML/XML tags from text, inserting spaces in their place::

      >>> striptags('<h1>title</h1>')
      ' title '
      >>> striptags('plain text')
      'plain text'
      >>> striptags(u'word<br>break')
      u'word break'
    """
    return retag.sub(' ', text)

def getwords(text, splitchars=resplit):
    """
    Get words in text by splitting text along specified splitchars
    and stripping out the splitchars::

      >>> getwords('this is some text.')
      ['this', 'is', 'some', 'text']
      >>> getwords('and/or')
      ['and', 'or']
      >>> getwords('one||two')
      ['one', 'two']
      >>> getwords("does not is doesn't")
      ['does', 'not', 'is', "doesn't"]
      >>> getwords(u'hola unicode!')
      [u'hola', u'unicode']
      >>> getwords('^break^me^', splitchars='^')
      ['break', 'me']

    It appears Python's doctest module defaults to Latin-1 even if the file
    encoding specifies UTF-8, so we can't run a test in here with non-ASCII
    characters. Suggestions on how to do this are welcome.
    """
    if isinstance(splitchars, basestring):
        splitchars = re.compile(_makecharregex(splitchars))

    # We can't simply use '\W+' because that will split along the apostrophe.
    result = splitchars.split(text)
    # Blank tokens will only be at beginning or end of text.
    if result[0] == '':
        result.pop(0)
    if result and result[-1] == '':
        result.pop(-1)
    return result

def getsentences(text):
    """
    Simplistic sentence splitter. Cuts input text at a period, exclamation or
    question mark. Not for serious use.

    >>> getsentences("This is a single sentence.")
    ['This is a single sentence']
    >>> getsentences("This is one sentence. This is another.")
    ['This is one sentence', 'This is another']
    """
    result = resplitsentence.split(text)
    if result[0] == '':
        result.pop(0)
    if result and result[-1] == '':
        result.pop(-1)
    return [sentence.strip() for sentence in result]

def worddiff(text1, text2):
    """
    Generator that returns words that have been added or removed.
    Ignores specified junk characters (default: common latin punctuation).

    Examples::

      >>> list(worddiff('original text', 'changed text'))
      [('-', 'original'), ('+', 'changed')]

    Words separated by markers are correctly identified::

      >>> list(worddiff('this and that', 'this and/or that'))
      [('+', 'or')]

    Changes in only punctuation are ignored::

      >>> list(worddiff('some text', 'some text.'))
      []

    """
    for item in difflib.ndiff(getwords(text1), getwords(text2)):
        if item.startswith('+ '):
            yield ('+', item[2:])
        elif item.startswith('- '):
            yield ('-', item[2:])

if __name__=='__main__':
    import sys
    if '-t' in sys.argv[1:]:
        import doctest
        doctest.testmod()
    else:
        if len(sys.argv) != 3:
            print "Syntax: %s file1 file2" % sys.argv[0]
        else:
            text1 = open(sys.argv[1], 'rb').read()
            text2 = open(sys.argv[2], 'rb').read()
            for result in worddiff(text1, text2):
                print result
