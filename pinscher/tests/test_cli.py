from tempdir import TempDir
import unittest
import os
import sqlite3
import hashlib

import pinscher.exceptions
import pinscher.cli


class TestCli(unittest.TestCase):

    def test_parse_path_with_hyphen(self):
        args = pinscher.cli.parse('init --keyfile-path here-to-here.keyfile --database-path -here-it-is.db --generate'.split(' '))
        self.assertEquals('here-to-here.keyfile', args['keyfile-path'])
        self.assertEquals('-here-it-is.db', args['database-path'])

    def test_parse_mode(self):
        args = pinscher.cli.parse('init --keyfile-path here.keyfile --database-path here.db --generate'.split(' '))
        assert args['mode'] == 'init'

    def test_validate_unknown_mode(self):
        self.assertRaises(pinscher.exceptions.InvalidArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('mode --keyfile-path here.keyfile --database-path here.db --generate'.split(' ')))

    def test_validate_unknown_arg(self):
        self.assertRaises(pinscher.exceptions.InvalidArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --unknown huh --keyfile-path here.keyfile --database-path here.db --generate'.split(' ')))

    def test_validate_missing_value(self):
        self.assertRaises(pinscher.exceptions.InvalidArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --keyfile-path here.keyfile --database-path here.db --generate --characters'.split(' ')))
        self.assertRaises(pinscher.exceptions.InvalidArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --keyfile-path here.keyfile --database-path here.db --characters --generate'.split(' ')))

    def test_validate_invalid_arg(self):
        self.assertRaises(pinscher.exceptions.InvalidArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --keyfile-path here.keyfile --database-path here.db --generate --length 0'.split(' ')))
        self.assertRaises(pinscher.exceptions.InvalidArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --keyfile-path here.keyfile --database-path here.db --generate --length -5'.split(' ')))
        self.assertRaises(pinscher.exceptions.InvalidArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --keyfile-path here.keyfile --database-path here.db --generate --length a'.split(' ')))

    def test_init_no_keyfile_path(self):
        self.assertRaises(pinscher.exceptions.MissingArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --database-path here.db --generate'.split(' ')))

    def test_init_no_database_path(self):
        self.assertRaises(pinscher.exceptions.MissingArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --keyfile-path here.keyfile --generate'.split(' ')))

    def test_init_no_key_or_generate(self):
        self.assertRaises(pinscher.exceptions.MissingArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --keyfile-path here.keyfile --database-path here.db'.split(' ')))

    def test_init_both_key_and_generate(self):
        self.assertRaises(pinscher.exceptions.InvalidArgument,
                          pinscher.cli.validate,
                          pinscher.cli.parse('init --keyfile-path here.keyfile --database-path here.db --generate --key aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --iv bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'.split(' ')))

    def test_generate_key_valid(self):
        key, iv = pinscher.cli.generate_key()
        self.assertTrue(pinscher.cli.args_defaults['init']['key']['valid'](key))
        self.assertTrue(pinscher.cli.args_defaults['init']['iv']['valid'](iv))

    def test_init_generate_if_no_key(self):
        self.generated = False

        def g():
            self.generated = True
            return 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        pinscher.cli.generate_key = g
        with TempDir() as d:
            keyfile = os.path.join(d.name, 'test.keyfile')
            database = os.path.join(d.name, 'test.database')
            args = 'init --keyfile-path %s --database-path %s --generate' % (keyfile, database,)
            pinscher.cli.main(args.split(' '))
            self.assertTrue(self.generated)

    def test_init_dont_generate_if_key(self):
        self.generated = False

        def g():
            self.generated = True
            return 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        pinscher.cli.generate_key = g
        with TempDir() as d:
            keyfile = os.path.join(d.name, 'test.keyfile')
            database = os.path.join(d.name, 'test.database')
            args = 'init --keyfile-path %s --database-path %s --key cccccccccccccccccccccccccccccccc --iv bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' % (keyfile, database,)
            pinscher.cli.main(args.split(' '))
            self.assertFalse(self.generated)

    def test_generate_key_not_identical(self):
        self.assertNotEqual(pinscher.cli.generate_key(), pinscher.cli.generate_key())

    def test_init_saves_keyfile(self):
        with TempDir() as d:
            keyfile = os.path.join(d.name, 'test.keyfile')
            database = os.path.join(d.name, 'test.database')
            key = 'cccccccccccccccccccccccccccccccc'
            iv = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
            length = '5'
            characters = 'abc'
            args = 'init --keyfile-path %s --database-path %s --key %s --iv %s --length %s --characters %s' % (keyfile, database, key, iv, length, characters)
            pinscher.cli.main(args.split(' '))
            with open(keyfile, 'r') as f:
                contents = f.read().splitlines()
                self.assertEqual(database, contents[0])
                self.assertEqual(key, contents[1])
                self.assertEqual(iv, contents[2])
                self.assertEqual(length, contents[3])
                self.assertEqual(characters, contents[4])

    def test_encrypt(self):
        key = 'cccccccccccccccccccccccccccccccc'
        iv = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        plaintext = 'test'
        ciphertext = pinscher.cli.encrypt(key, iv, plaintext)
        self.assertEqual(plaintext, pinscher.cli.decrypt(key, iv, ciphertext))

    def test_init_database_from_schema(self):
        db = pinscher.cli.init_database()
        cursor = db.cursor()
        results = cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
        self.assertIn(('Credentials',), results)
        cursor.execute('SELECT * FROM Credentials')
        cursor.fetchone()
        columns = [d[0] for d in cursor.description]
        for c in ['domain', 'username', 'password', 'iv']:
            self.assertIn(c, columns)
        cursor.close()

    def test_init_saves_database(self):
        with TempDir() as d:
            keyfile = os.path.join(d.name, 'test.keyfile')
            database = os.path.join(d.name, 'test.database')
            key = 'cccccccccccccccccccccccccccccccc'
            iv = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
            length = '5'
            characters = 'abc'
            args = 'init --keyfile-path %s --database-path %s --key %s --iv %s --length %s --characters %s' % (keyfile, database, key, iv, length, characters)
            pinscher.cli.main(args.split(' '))
            with open(database, 'r') as f:
                ciphersql = f.read()
                sql = pinscher.cli.decrypt(key, iv, ciphersql)
                connection = sqlite3.connect(':memory:')
                cursor = connection.cursor()
                cursor.executescript(sql)
                results = cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
                self.assertIn(('Credentials',), results)
                cursor.execute('SELECT * FROM Credentials')
                cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]
                for c in ['domain', 'username', 'password', 'iv']:
                    self.assertIn(c, columns)
                cursor.close()

    def test_load_keyfile(self):
        with TempDir() as d:
            details = {'keyfile-path': os.path.join(d.name, 'test.keyfile'),
                       'database-path': os.path.join(d.name, 'test.database'),
                       'key': 'cccccccccccccccccccccccccccccccc',
                       'iv': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
                       'length': 5,
                       'characters': 'abc'
                       }
            pinscher.cli.save_keyfile(details)
            self.assertEqual(details, pinscher.cli.load_keyfile(details['keyfile-path']))

    def test_add_works(self):
        with TempDir() as d:
            keyfile = os.path.join(d.name, 'test.keyfile')
            database = os.path.join(d.name, 'test.database')
            key = 'cccccccccccccccccccccccccccccccc'
            iv = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
            args = 'init --keyfile-path %s --database-path %s --key %s --iv %s' % (keyfile, database, key, iv,)
            pinscher.cli.main(args.split(' '))
            domain = 'domain'
            username = 'username'
            password = 'password'
            pin = '1234'
            args = 'add  --keyfile-path %s --domain %s --username %s --password %s --pin %s' % (keyfile, domain, username, password, pin)
            pinscher.cli.main(args.split(' '))
            with open(database, 'r') as f:
                ciphersql = f.read()
                sql = pinscher.cli.decrypt(key, iv, ciphersql)
                connection = sqlite3.connect(':memory:')
                cursor = connection.cursor()
                cursor.executescript(sql)
                cursor.execute('SELECT domain, username, password, iv FROM Credentials')
                row = cursor.fetchone()
                self.assertEqual(domain, row[0])
                self.assertEqual(username, row[1])
                self.assertEqual(password, pinscher.cli.decrypt(hashlib.sha256(domain + username + pin).digest().encode('hex'), row[3], row[2]))
                cursor.close()

    def test_add_generate_password(self):
        password = pinscher.cli.generate_password(5, 'abc')
        self.assertEqual(5, len(password))
        self.assertTrue(False not in [(c in 'abc') for c in password])

    def test_load_database(self):
        with TempDir() as d:
            keyfile = os.path.join(d.name, 'test.keyfile')
            database = os.path.join(d.name, 'test.database')
            args = 'init --keyfile-path %s --database-path %s --generate' % (keyfile, database,)
            pinscher.cli.main(args.split(' '))
            k = pinscher.cli.load_keyfile(keyfile)
            db = pinscher.cli.load_database(k)
            cursor = db.cursor()
            results = cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
            self.assertIn(('Credentials',), results)
            cursor.execute('SELECT * FROM Credentials')
            cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            for c in ['domain', 'username', 'password', 'iv']:
                self.assertIn(c, columns)
            cursor.close()

    def test_find_works(self):
        with TempDir() as d:
            keyfile = os.path.join(d.name, 'test.keyfile')
            database = os.path.join(d.name, 'test.database')
            key = 'cccccccccccccccccccccccccccccccc'
            iv = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
            args = 'init --keyfile-path %s --database-path %s --key %s --iv %s' % (keyfile, database, key, iv,)
            pinscher.cli.main(args.split(' '))
            domain = 'domain'
            username = 'username'
            password = 'password'
            pin = '1234'
            args = 'add  --keyfile-path %s --domain %s --username %s --password %s --pin %s' % (keyfile, domain, username, password, pin)
            pinscher.cli.main(args.split(' '))
            domain = 'dom'
            username = 'user'
            pin = '1234'
            args = 'find  --keyfile-path %s --domain %s --username %s --pin %s' % (keyfile, domain, username, pin)
            result = pinscher.cli.main(args.split(' '))
            self.assertEqual(result, password)
