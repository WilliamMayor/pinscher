import os

import alp
from alp.item import Item as I
from alp.settings import Settings

from pinscher.Keyfile import Keyfile
from pinscher.Database import Database


def find_credentials(keyfiles, query):
    matches = {}
    exact = {}
    for k in keyfiles:
        with Database(k) as d:
            if len(query) == 1:
                matches[k] = d.find(domain=query[0]) + d.find(username=query[0])
            else:
                for c in d.find(domain=query[0], username=query[1]) + d.find(domain=query[1], username=query[0]):
                    if c.domain == query[0] and c.username == query[1]:
                        exact[k] = c
                    else:
                        v = matches.get(k, [])
                        v.append(c)
                        matches[k] = v
    return exact, matches


def find_keyfiles(keyfiles, query):
    matches = []
    exact = None
    for k in keyfiles:
        if query[0] == k.name:
            exact = k.name
        elif query[0] in k.name:
            matches.append(k)
    return exact, matches


def load_keyfiles():
    s = Settings()
    raw_k = s.get('keyfiles', {})
    keyfiles = []
    for name in raw_k:
        try:
            k = Keyfile.load(raw_k[name])
            k.name = name
            keyfiles.append(k)
        except:
            pass
    return keyfiles


def query_one(query):
    """keyfile|domain|username"""
    items = []
    keyfiles = load_keyfiles()
    exact_c, match_c = find_credentials(keyfiles, query)
    exact_k, match_k = find_keyfiles(keyfiles, query)
    for k in match_c:
        for c in match_c[k]:
            items.append(I(
                title='%s:%s' % (c.username, c.domain),
                subtitle='Use this account (need PIN)',
                autocomplete='%s %s ' % (c.domain, c.username),
                valid=False
            ))
    items.append(I(
        title='New account %s' % (query[0]),
        subtitle='Add new account (need username)',
        autocomplete='%s ' % (query[0]),
        valid=False
    ))
    if exact_k is None:
        items.append(I(
            title='Create new keyfile: %s' % query[0],
            subtitle='Create a new keyfile',
            arg='create %s' % query[0],
            valid=True
        ))
    return items


def query_two(query):
    """keyfile|domain|username username|domain|keyfile_path"""
    items = []
    keyfiles = load_keyfiles()
    exact_c, match_c = find_credentials(keyfiles, query)
    exact_k, match_k = find_keyfiles(keyfiles, query)
    for k in match_c:
        for c in match_c[k]:
            items.append(I(
                title='%s:%s' % (c.username, c.domain),
                subtitle='Use this account (need PIN)',
                autocomplete='%s %s ' % (c.domain, c.username),
                valid=False
            ))
    if not exact_c:
        items.append(I(
            title='Create new account %s:%s' % (query[1], query[0]),
            subtitle='Create new account (need PIN)',
            autocomplete='%s %s ' % (query[0], query[1]),
            valid=False
        ))
    for k in exact_c:
        c = exact_c[k]
        items.append(I(
            title='%s:%s' % (c.username, c.domain),
            subtitle='Use this account (need PIN)',
            autocomplete='%s %s ' % (c.domain, c.username),
            valid=False
        ))
    if exact_k is None:
        items.append(I(
            title='Create new keyfile: %s' % query[0],
            subtitle='Save keyfile here: %s' % query[1],
            arg='create %s %s' % (query[0], query[1]),
            valid=True
        ))
    return items


def query_three(query):
    """keyfile|domain|username username|domain|keyfile_path pin|database_path"""
    items = []
    keyfiles = load_keyfiles()
    exact_c, match_c = find_credentials(keyfiles, query)
    exact_k, match_k = find_keyfiles(keyfiles, query)
    for k in exact_c:
        c = exact_c[k]
        items.append(I(
            title='Copy password %s:%s from %s' % (query[1], query[0], k.name),
            subtitle='Copy to clipboard',
            arg='copy %s %s %s %s ' % (k.path, query[0], query[1], query[2]),
            valid=True
        ))
        items.append(I(
            title='Update account %s:%s in %s' % (query[1], query[0], k.name),
            subtitle='Randomly generate a new password',
            arg='update %s %s %s %s ' % (k.path, query[0], query[1], query[2]),
            valid=True
        ))
        items.append(I(
            title='Delete account %s:%s in %s' % (query[1], query[0], k.name),
            subtitle='Remove this username and password',
            arg='delete %s %s %s' % (k.path, query[0], query[1]),
            valid=True
        ))
    if not exact_c:
        for k in keyfiles:
            items.append(I(
                title='Save new account %s:%s in %s' % (query[1], query[0], k.name),
                subtitle='Randomly generate a password',
                arg='add %s %s %s %s ' % (k.path, query[0], query[1], query[2]),
                valid=True
            ))
    for k in match_c:
        for c in match_c[k]:
            items.append(I(
                title='Copy password %s:%s from %s' % (c.username, c.domain, k.name),
                subtitle='Copy to clipboard',
                arg='copy %s %s %s %s ' % (k.path, c.domain, c.username, query[2]),
                valid=True
            ))
            items.append(I(
                title='Update account %s:%s in %s' % (c.username, c.domain, k.name),
                subtitle='Randomly generate a new password',
                arg='update %s %s %s %s ' % (k.path, c.domain, c.username, query[2]),
                valid=True
            ))
            items.append(I(
                title='Delete account %s:%s in %s' % (c.username, c.domain, k.name),
                subtitle='Remove this username and password',
                arg='delete %s %s %s' % (k.path, c.domain, c.username),
                valid=True
            ))
    if exact_k is None:
        items.append(I(
            title='Create new keyfile: %s' % query[0],
            subtitle='Save database here: %s' % query[2],
            arg='create %s %s %s' % (query[0], query[1], query[2]),
            valid=True
        ))
    return items


def query_four(query):
    """keyfile|domain|username username|domain|keyfile_path pin|database_path password|length|characters"""
    items = []
    keyfiles = load_keyfiles()
    exact_c, match_c = find_credentials(keyfiles, query)
    exact_k, match_k = find_keyfiles(keyfiles, query)
    for k in exact_c:
        c = exact_c[k]
        items.append(I(
            title='Update account %s:%s in %s' % (query[1], query[0], k.name),
            subtitle='Set password to %s' % query[3],
            arg='update %s %s %s %s %s' % (k.path, query[0], query[1], query[2], query[3]),
            valid=True
        ))
        try:
            length = int(query[3])
            items.append(I(
                title='Update account %s:%s in %s' % (query[1], query[0], k.name),
                subtitle='Randomly generate a %d character password' % length,
                arg='update %s %s %s %s p %s' % (k.path, query[0], query[1], query[2], query[3]),
                valid=True
            ))
        except:
            items.append(I(
                title='Update account %s:%s in %s' % (query[1], query[0], k.name),
                subtitle='Randomly generate a password containing only characters from %s' % query[3],
                arg='update %s %s %s %s p %d %s' % (k.path, query[0], query[1], query[2], k.length, query[3]),
                valid=True
            ))
    if not exact_c:
        for k in keyfiles:
            try:
                length = int(query[3])
                items.append(I(
                    title='Save new account %s:%s in %s' % (query[1], query[0], k.name),
                    subtitle='Randomly generate a %d character password' % length,
                    arg='add %s %s %s %s p %s' % (k.path, query[0], query[1], query[2], query[3]),
                    valid=True
                ))
            except:
                items.append(I(
                    title='Save new account %s:%s in %s' % (query[1], query[0], k.name),
                    subtitle='Randomly generate a password containing only characters from %s' % query[3],
                    arg='add %s %s %s %s p %d %s' % (k.path, query[0], query[1], query[2], k.length, query[3]),
                    valid=True
                ))
    for k in match_c:
        for c in match_c[k]:
            items.append(I(
                title='Update account %s:%s in %s' % (c.username, c.domain, k.name),
                subtitle='Set password to %s' % query[3],
                arg='update %s %s %s %s %s' % (k.path, c.domain, c.username, query[2], query[3]),
                valid=True
            ))
            try:
                length = int(query[3])
                items.append(I(
                    title='Update account %s:%s in %s' % (c.username, c.domain, k.name),
                    subtitle='Randomly generate a %d character password' % length,
                    arg='update %s %s %s %s p %s' % (k.path, c.domain, c.username, query[2], query[3]),
                    valid=True
                ))
            except:
                items.append(I(
                    title='Update account %s:%s in %s' % (c.username, c.domain, k.name),
                    subtitle='Randomly generate a password containing only characters from %s' % query[3],
                    arg='update %s %s %s %s p %d %s' % (k.path, c.domain, c.username, query[2], k.length, query[3]),
                    valid=True
                ))
    if exact_k is None:
        try:
            length = int(query[3])
            items.append(I(
                title='Create new keyfile: %s' % query[0],
                subtitle='Passwords in this database should be %d characters long' % length,
                arg='create %s %s %s %s %s' % (k.path, query[0], query[1], query[2], query[3]),
                valid=True
            ))
        except:
            items.append(I(
                title='Create new keyfile: %s' % query[0],
                subtitle='Passwords in this database should only contain characters in %s' % query[3],
                arg='create %s %s %s %s %d %s' % (k.path, query[0], query[1], query[2], Keyfile.LENGTH, query[3]),
                valid=True
            ))
    return items


def query_five(query):
    """keyfile|domain|username username|domain|keyfile_path pin|database_path password|length|characters characters|length"""
    items = []
    keyfiles = load_keyfiles()
    exact_c, match_c = find_credentials(keyfiles, query)
    exact_k, match_k = find_keyfiles(keyfiles, query)
    try:
        length = int(query[3])
        characters = query[4]
    except:
        try:
            length = int(query[4])
            characters = query[3]
        except:
            return [I(title='Unknown input', subtitle='I don\'t know what you mean... sorry.', valid=False)]
    for k in exact_c:
        c = exact_c[k]
        items.append(I(
            title='Update account %s:%s in %s' % (query[1], query[0], k.name),
            subtitle='Randomly generate a %d character password containing only characters from %s' % (length, characters),
            arg='update %s %s %s %s p %d %s' % (k.path, query[0], query[1], query[2], length, characters),
            valid=True
        ))
    if not exact_c:
        for k in keyfiles:
            items.append(I(
                title='Save new account %s:%s in %s' % (query[1], query[0], k.name),
                subtitle='Randomly generate a password a %d character password containing only characters from %s' % (length, characters),
                arg='add %s %s %s %s p %d %s' % (k.path, query[0], query[1], query[2], length, characters),
                valid=True
            ))
    for k in match_c:
        for c in match_c[k]:
            items.append(I(
                title='Update account %s:%s in %s' % (c.username, c.domain, k.name),
                subtitle='Randomly generate a password a %d character password containing only characters from %s' % (length, characters),
                arg='update %s %s %s %s p %d %s' % (k.path, c.domain, c.username, query[2], length, characters),
                valid=True
            ))
    if exact_k is None:
        items.append(I(
            title='Create new keyfile: %s' % query[0],
            subtitle='Passwords in this database should be %d characters long and only contain characters in %s' % (length, characters),
            arg='create %s %s %s %s %d %s' % (k.path, query[0], query[1], query[2], length, characters),
            valid=True
        ))
    return items

actions = [query_one, query_two, query_three, query_four, query_five]


if __name__ == '__main__':
    query = alp.args()
    try:
        items = actions[len(query)-1](query)
    except IndexError:
        items = [I(title='Unknown input', subtitle='I don\'t know what you mean... sorry.', valid=False)]
    if len(items) == 0:
        items.append(I(
            title='Nothing found',
            subtitle='Your query didn\'t match anything. Sorry',
            valid=False))
    alp.feedback(items)
