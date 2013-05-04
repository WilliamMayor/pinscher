import string
import sys
import sqlite3
import traceback
import hashlib
from pkg_resources import resource_string

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Random import random

import exceptions

args_defaults = {
    'init': {
        'keyfile-path': {'required': True},
        'database-path': {'required': True},
        'key': {'xor': 'generate', 'valid': lambda value: AES.key_size[0] <= len(value.decode('hex')) <= AES.key_size[-1]},
        'iv': {'default': Random.new().read(AES.block_size).encode('hex'), 'valid': lambda value: len(value.decode('hex')) == AES.block_size},
        'generate': {'flag': True, 'xor': 'key'},
        'length': {'default': 32, 'valid': lambda value: int(value) > 0},
        'characters': {'default': string.digits + string.letters + string.punctuation + ' ', 'valid': lambda value: len(value) > 0}
    }, 'add': {
        'keyfile-path': {'required': True},
        'domain': {'required': True},
        'username': {'required': True},
        'password': {'xor': 'generate'},
        'generate': {'flag': True, 'xor': 'password'},
        'length': {'default': 32, 'valid': lambda value: int(value) > 0},
        'characters': {'default': string.digits + string.letters + string.punctuation + ' ', 'valid': lambda value: len(value) > 0},
        'pin': {'required': True}
    }, 'find': {
        'keyfile-path': {'required': True},
        'domain': {'or': 'username'},
        'username': {'or': 'domain'},
        'pin': {'required': True}
    }
}


def parse(raw_args):
    args = {}
    args['mode'] = raw_args[0]
    for i in range(1, len(raw_args)):
        if raw_args[i].startswith('--'):
            name = raw_args[i][2:]
            if len(raw_args) > i+1 and not raw_args[i+1].startswith('--'):
                args[name] = raw_args[i+1]
                i += 1
            else:
                args[name] = None
    return args


def validate(args):
    if args['mode'] not in args_defaults.keys():
        raise exceptions.InvalidArgument('Unrecognised mode %s, valid values are %s' % (args['mode'], args_defaults.keys(),))
    for arg in args_defaults[args['mode']]:
        details = args_defaults[args['mode']][arg]
        if arg not in args.keys():
            if 'default' in details:
                args[arg] = details['default']
            elif 'xor' in details and details['xor'] not in args:
                raise exceptions.MissingArgument('Must have one of --%s or --%s' % (arg, details['xor']))
            elif details.get('required', False):
                raise exceptions.MissingArgument('--%s is required' % (arg,))
    for arg, value in [(a, v) for a, v in args.iteritems() if a != 'mode']:
        if arg not in args_defaults[args['mode']].keys():
            raise exceptions.InvalidArgument('Unrecognised argument --%s, valid values are %s' % (arg, args_defaults[args['mode']].keys(),))
        details = args_defaults[args['mode']][arg]
        if value is None and 'flag' not in details:
            raise exceptions.InvalidArgument('Missing value for --%s' % (arg,))
        if 'valid' in details:
            try:
                if not details['valid'](value):
                    raise exceptions.InvalidArgument()
            except (exceptions.InvalidArgument, ValueError):
                raise exceptions.InvalidArgument('Invalid argument: --%s %s' % (arg, value,))
        if 'xor' in details and details['xor'] in args:
            print 'xor'
            raise exceptions.InvalidArgument('Cannot have both --%s and --%s' % (arg, details['xor']))


def generate_key():
    key = Random.new().read(AES.key_size[-1])
    iv = Random.new().read(AES.block_size)
    return (s.encode('hex') for s in (key, iv))


def generate_password(length, characters):
    password = []
    for i in xrange(0, length):
        password += random.choice(characters)
    return ''.join(password)


def save_keyfile(details):
    with open(details['keyfile-path'], 'w') as f:
        f.write(details['database-path'])
        f.write('\n')
        f.write(details['key'])
        f.write('\n')
        f.write(details['iv'])
        f.write('\n')
        f.write(str(details['length']))
        f.write('\n')
        f.write(details['characters'])


def load_keyfile(path):
    details = {'keyfile-path': path}
    with open(path, 'r') as f:
        details['database-path'] = f.readline().strip()
        details['key'] = f.readline().strip()
        details['iv'] = f.readline().strip()
        details['length'] = int(f.readline().strip())
        details['characters'] = f.readline().strip()
    return details


def encrypt(key, iv, plaintext):
    cipher = AES.new(key.decode('hex'), AES.MODE_CFB, iv.decode('hex'))
    return cipher.encrypt(plaintext).encode('hex')


def decrypt(key, iv, ciphertext):
    cipher = AES.new(key.decode('hex'), AES.MODE_CFB, iv.decode('hex'))
    return cipher.decrypt(ciphertext.decode('hex'))


def init_database():
    connection = sqlite3.connect(':memory:')
    schema = resource_string(__name__, 'schema.sql')
    connection.executescript(schema)
    return connection


def save_database(connection, details):
    with open(details['database-path'], 'wb') as f:
        f.write(encrypt(details['key'], details['iv'], '\n'.join(connection.iterdump())))


def load_database(details):
    with open(details['database-path'], 'rb') as f:
        sql = decrypt(details['key'], details['iv'], f.read())
    connection = sqlite3.connect(':memory:')
    connection.executescript(sql)
    return connection


def add_credentials(db, details):
    key = hashlib.sha256(details['domain'] + details['username'] + details['pin']).digest().encode('hex')
    iv = Random.new().read(AES.block_size).encode('hex')
    ciphertext = encrypt(key, iv, details['password'])
    cursor = db.cursor()
    cursor.execute('INSERT INTO Credentials(domain, username, password, iv) VALUES(?,?,?,?)', (details['domain'], details['username'], ciphertext, iv))


def run(args):
    if args['mode'] == 'init':
        if 'generate' in args:
            args['key'], args['iv'] = generate_key()
        save_keyfile(args)
        db = init_database()
        save_database(db, args)
    if args['mode'] == 'add':
        keyfile = load_keyfile(args['keyfile-path'])
        if 'generate' in args:
            args['password'] = generate_password(int(args.get('length', keyfile['length'])), args.get('characters', keyfile['characters']))
        db = load_database(keyfile)
        add_credentials(db, args)
        save_database(db, keyfile)


def main(raw_args):
    try:
        args = parse(raw_args)
        validate(args)
        run(args)
    except Exception as e:
        print 'There was an error:', e
        print traceback.format_exc()


def script_entry_point():
    main(sys.argv[1:])

if __name__ == '__main__':
    script_entry_point()
