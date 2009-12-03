import doctest

import interfaces, page, revision, site, user, utils

if __name__=='__main__':
    for module in interfaces, page, revision, site, user, utils:
        doctest.testmod(module)
