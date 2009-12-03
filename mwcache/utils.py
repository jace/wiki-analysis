"""
Helper routes for dealing with date/time strings and other things.
"""
import re
import datetime

MWDATEFMT = '%Y-%m-%dT%H:%M:%SZ'


def mwdatetime(text):
    """
    Convert a MediaWiki datetime string into a Python datetime object.

    >>> mwdatetime('2009-11-02T15:57:01Z')
    datetime.datetime(2009, 11, 2, 15, 57, 1)
    """
    return datetime.datetime.strptime(text, MWDATEFMT)


def parsedate(text):
    """
    Parse a typical human-friendly datetime string into a Python datetime object.

    >>> isinstance(parsedate('now'), datetime.datetime)
    True
    >>> isinstance(parsedate('today'), datetime.datetime)
    True
    >>> isinstance(parsedate('yesterday'), datetime.datetime)
    True
    >>> parsedate('2009-01-01')
    datetime.datetime(2009, 1, 1, 0, 0)
    """
    if text == 'now':
        return datetime.datetime.utcnow()
    elif text == 'today':
        return datetime.datetime.today()
    elif text == 'yesterday':
        return datetime.datetime.today() - datetime.timedelta(days=1)
    else:
        try:
            return datetime.datetime.strptime(text, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.datetime.strptime(text, '%Y/%m/%d')
            except ValueError:
                try:
                    return datetime.datetime.strptime(text, '%d-%m-%Y')
                except ValueError:
                    return datetime.datetime.strptime(text, '%d/%m/%Y')


periodflags = {
    'w': 'weeks',
    'd': 'days',
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds',
    }


def parseperiod(text):
    """
    Parse a date period in the form of "5d3h" and return a timedelta object.

    >>> parseperiod('5h')
    datetime.timedelta(0, 18000)
    >>> parseperiod('5h4m')
    datetime.timedelta(0, 18240)
    >>> parseperiod('5 h 4 m')
    datetime.timedelta(0, 18240)
    >>> parseperiod('1w')
    datetime.timedelta(7)
    >>> parseperiod('10d5h')
    datetime.timedelta(10, 18000)
    >>> parseperiod('1y')
    Traceback (most recent call last):
    ...
    ValueError: Unrecognised period identifier in "1y".
    >>> parseperiod(' 5h ')
    datetime.timedelta(0, 18000)
    """
    parts = filter(None, [part.strip() for part in re.split('(\d+)', text)])
    if len(parts) % 2 != 0:
        raise ValueError('Invalid time period "%s".' % text)
    parms = dict(map(lambda x,y:(periodflags.get(y, None), int(x)),
                      parts[0::2], parts[1::2]))
    if None in parms:
        raise ValueError('Unrecognised period identifier in "%s".' % text)
    return datetime.timedelta(**parms)


if __name__=='__main__':
    import doctest
    doctest.testmod()
