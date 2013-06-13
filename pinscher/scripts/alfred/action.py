import subprocess

import alp
from alp.settings import Settings

import pinscher.utilities
from pinscher.Keyfile import Keyfile
from pinscher.Database import Database
from pinscher.Credentials import Credentials


def notify(subtitle, message):
    print '\n'.join([subtitle, message])


def pbcopy(text):
    p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    p.stdin.write(text)


def create(name, keyfile_path=None, database_path=None, length=Keyfile.LENGTH, characters=Keyfile.CHARACTERS):
    try:
        if keyfile_path is None:
            keyfile_path = '%s.pkf' % name
        if database_path is None:
            database_path = '%s.pdb' % name
        keyfile = Keyfile.create(
            keyfile_path,
            database_path,
            length=length,
            characters=characters)
        Database.create(keyfile)
        s = Settings()
        keyfiles = s.get('keyfiles', {})
        keyfiles[name] = keyfile.path
        s.set(keyfiles=keyfiles)
        notify('Created the keyfile', 'and initialised a database')
    except:
        notify('Error', 'Could not create the keyfile')


def copy(keyfile_path, domain, username, pin):
    try:
        k = Keyfile.load(keyfile_path)
        with Database(k) as d:
            results = d.find(domain=domain, username=username)
        pbcopy(results[0].unlock(pin))
        notify('Copied!', 'Password copied to clipboard')
    except:
        notify('Error', 'Could not copy password')


def update(keyfile_path, domain, username, pin, password=None, length=None, characters=None):
    try:
        k = Keyfile.load(keyfile_path)
        if password is None or length is not None:
            args = {}
            if length is not None:
                args['length'] = length
            if characters is not None:
                args['characters'] = characters
            password = pinscher.utilities.generate_password(k, args)
        c = Credentials(domain, username, plainpassword=password)
        with Database(k) as d:
            d.update(c, pin)
        pbcopy(c.unlock(pin))
        notify('Updated!', 'Password updated and copied to clipboard')
    except:
        notify('Error', 'Could not update password')


def delete(keyfile_path, domain, username):
    try:
        k = Keyfile.load(keyfile_path)
        c = Credentials(domain, username)
        with Database(k) as d:
            d.delete(c)
        notify('Deleted!', 'Account %s@%s deleted' % (username, domain))
    except:
        notify('Error', 'Could not update password')


def add(keyfile_path, domain, username, pin, password=None, length=None, characters=None):
    try:
        k = Keyfile.load(keyfile_path)
        if password is None or length is not None:
            args = {}
            if length is not None:
                args['length'] = length
            if characters is not None:
                args['characters'] = characters
            password = pinscher.utilities.generate_password(k, args)
        c = Credentials(domain, username, plainpassword=password)
        with Database(k) as d:
            d.add(c, pin)
        pbcopy(c.unlock(pin))
        notify('Added!', 'Password copied to clipboard')
    except Exception as e:
        print e
        notify('Error', 'Could not add password')

actions = {
    'create': create,
    'copy': copy,
    'update': update,
    'delete': delete,
    'add': add
}

if __name__ == '__main__':
    query = alp.args()
    actions[query[0]](*query[1:])
