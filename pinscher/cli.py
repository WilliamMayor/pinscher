import string
import sys
import sqlite3
import traceback
from pkg_resources import resource_string

from Crypto.Cipher import AES
from Crypto import Random

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


def encrypt(key, iv, plaintext):
    cipher = AES.new(key.decode('hex'), AES.MODE_CFB, iv.decode('hex'))
    return cipher.encrypt(plaintext)


def decrypt(key, iv, ciphertext):
    cipher = AES.new(key.decode('hex'), AES.MODE_CFB, iv.decode('hex'))
    return cipher.decrypt(ciphertext)


def init_database():
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()
    schema = resource_string(__name__, 'schema.sql')
    cursor.executescript(schema)
    cursor.close()
    return connection


def save_database(connection, args):
    with open(args['database-path'], 'wb') as f:
        f.write(encrypt(args['key'], args['iv'], '\n'.join(connection.iterdump())))


def run(args):
    if args['mode'] == 'init':
        if 'generate' in args:
            args['key'], args['iv'] = generate_key()
        save_keyfile(args)
        db = init_database()
        save_database(db, args)


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
