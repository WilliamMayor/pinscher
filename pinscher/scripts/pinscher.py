"""pinscher.

Usage:
    pinscher init KEYFILE DATABASE [--key KEY] [--iv IV] [--length LENGTH] [--characters CHARACTERS]
    pinscher add KEYFILE --domain DOMAIN --username USERNAME --pin PIN [--password PASSWORD] [--length LENGTH] [--characters CHARACTERS]
    pinscher find KEYFILE... [--domain DOMAIN] [--username USERNAME] [--pin PIN]
    pinscher update KEYFILE --domain DOMAIN --username USERNAME --pin PIN [--password PASSWORD] [--length LENGTH] [--characters CHARACTERS]
    pinscher delete KEYFILE --domain DOMAIN --username USERNAME
    pinscher --help
    pinscher --version

Options:
    --help                   Show this message
    --version                Show the version
    --key KEY                The hex encoded, 256-bit private AES key, used to encrypt the database.
    --iv IV                  The hex encoded, 96-bit iv, used to seed the encryption.
    --length LENGTH          The length of generated passwords [default: 32].
    --characters CHARACTERS  The characters to use when generating passwords.
    --domain DOMAIN          The domain to register the credentials to.
    --username USERNAME      The username of the credentials to store.
    --pin PIN                The pin used to further encrypt the password in the database.
    --password PASSWORD      The password to encrypt and store.

"""

import sys
import re

import docopt

import pinscher.utilities as utilities
from pinscher.Keyfile import Keyfile
from pinscher.Database import Database
from pinscher.Credentials import Credentials


def sanitise(args):
    args = dict(
        (re.sub('^--', '', key).lower(), value)
        for key, value in args.iteritems() if bool(value))
    if 'length' in args:
        args['length'] = int(args['length'])
    return args


def pretty_credentials(c):
    if len(c) == 1:
        return '\n'.join([c[0].domain, c[0].username, c[0].plainpassword])
    return '\n\n'.join(['\n'.join([d.domain, d.username]) for d in c])


def run_init(args):
    keyfile = Keyfile.create(args['keyfile'][0], args['database'], **args)
    Database.create(keyfile)


def run_add(args):
    keyfile = Keyfile.load(args['keyfile'][0])
    with Database(keyfile) as d:
        c = Credentials(
            args['domain'],
            args['username'],
            plainpassword=args.get(
                'password',
                utilities.generate_password(keyfile, args)))
        d.add(c, args['pin'])
    return pretty_credentials([c])


def run_update(args):
    keyfile = Keyfile.load(args['keyfile'][0])
    with Database(keyfile) as d:
        c = Credentials(
            args['domain'],
            args['username'],
            plainpassword=args.get(
                'password',
                utilities.generate_password(keyfile, args)))
        d.update(c, args['pin'])
    return pretty_credentials([c])


def run_find(args):
    results = []
    for k in args['keyfile']:
        keyfile = Keyfile.load(k)
        with Database(keyfile) as d:
            results += d.find(args.get('domain', ''), args.get('username', ''))
    if len(results) == 1:
        if 'pin' in args:
            results[0].unlock(int(args['pin']))
    return pretty_credentials(results)


def run_delete(args):
    keyfile = Keyfile.load(args['keyfile'][0])
    with Database(keyfile) as d:
        c = Credentials(
            args['domain'],
            args['username'])
        d.delete(c)


def run(args):
    if 'init' in args:
        return run_init(args)
    if 'add' in args:
        return run_add(args)
    if 'find' in args:
        return run_find(args)
    if 'update' in args:
        return run_update(args)
    if 'delete' in args:
        return run_delete(args)


def main(raw_args):
    args = docopt.docopt(__doc__, argv=raw_args, version='pinscher 0.2dev')
    try:
        args = sanitise(args)
    except Exception as e:
        raise docopt.DocoptExit(
            'Invalid arguments (could not sanitise): %s' % e)
    try:
        return run(args)
    except Exception as e:
        raise docopt.DocoptExit('Failed to run: %s' % e)


def script_entry_point():
    results = main(sys.argv[1:])
    if results:
        print results

if __name__ == '__main__':
    script_entry_point()
