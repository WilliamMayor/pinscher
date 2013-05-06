from tempdir import TempDir
import unittest
import os

from utilities import not_raises

import pinscher.scripts.cli as cli
from pinscher.Keyfile import Keyfile
from pinscher.Database import Database


class TestCli(unittest.TestCase):

    key = '0b660492d98c54412d3d91818de5a2ae0b3110850a12010768b80fb277f55aa6'.decode('hex')
    iv = '9059d464b93397a2a98e8e1f00b596c6'.decode('hex')
    length = 5
    characters = 'abc'
    domain = 'domain'
    username = 'username'
    password = 'password'
    pin = '1234'

    def setUp(self):
        self.d = TempDir()
        self.k = os.path.join(self.d.name, 'keyfile')
        d = os.path.join(self.d.name, 'database')
        cli.main(('init %s %s' % (self.k, d)).split(' '))
        self.keyfile = Keyfile.load(self.k)

    def tearDown(self):
        self.d.dissolve()

    @not_raises(AttributeError)
    def test_init_defaults(self):
        with TempDir() as d:
            k = os.path.join(d.name, 'keyfile')
            d = os.path.join(d.name, 'database')
            cli.main(('init %s %s' % (k, d)).split(' '))
            keyfile = Keyfile.load(k)
            self.assertEqual(k, keyfile.path)
            self.assertEqual(d, keyfile.database_path)
            self.assertEqual(Keyfile.LENGTH, keyfile.length)
            self.assertEqual(Keyfile.CHARACTERS, keyfile.characters)
            keyfile.key
            keyfile.iv

    def test_init_override(self):
        with TempDir() as d:
            k = os.path.join(d.name, 'keyfile')
            d = os.path.join(d.name, 'database')
            cli.main(('init %s %s --key %s --iv %s --length %d --characters %s' % (k, d, self.key, self.iv, self.length, self.characters)).split(' '))
            keyfile = Keyfile.load(k)
            self.assertEqual(k, keyfile.path)
            self.assertEqual(d, keyfile.database_path)
            self.assertEqual(self.length, keyfile.length)
            self.assertEqual(self.characters, keyfile.characters)
            self.assertEqual(self.key, keyfile.key)
            self.assertEqual(self.iv, keyfile.iv)

    def test_add_defaults(self):
        results = cli.main(
            ('add %s --domain %s --username %s --pin %s'
                % (self.k, self.domain, self.username, self.pin)).split(' '))
        with Database(self.keyfile) as d:
            c = d.find(domain=self.domain, username=self.username)[0]
        c.unlock(self.pin)
        self.assertEqual(results, '\n'.join([c.domain, c.username, c.plainpassword]))

    def test_add_override(self):
        results = cli.main(
            ('add %s --domain %s --username %s --pin %s --length %d --characters %s'
                % (self.k, self.domain, self.username, self.pin, self.length, self.characters)).split(' '))
        parts = results.split('\n')
        self.assertEqual(self.length, len(parts[2]))
        for c in parts[2]:
            self.assertIn(c, self.characters)

    def test_add_provide_password(self):
        results = cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        parts = results.split('\n')
        self.assertEqual(self.password, parts[2])

    def test_find_single_keyfile_single_result(self):
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        results = cli.main(
            ('find %s --domain %s --username %s --pin %s'
                % (self.k, self.domain, self.username, self.pin)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, self.password]))

    def test_find_single_keyfile_multiple_results(self):
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain + '2', self.username, self.pin, self.password)).split(' '))
        results = cli.main(
            ('find %s --domain %s --username %s --pin %s'
                % (self.k, self.domain, self.username, self.pin)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, '', self.domain + '2', self.username]))

    def test_find_multiple_keyfiles_single_result(self):
        k2 = os.path.join(self.d.name, 'keyfile2')
        d2 = os.path.join(self.d.name, 'database2')
        cli.main(('init %s %s' % (k2, d2)).split(' '))
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        results = cli.main(
            ('find %s %s --domain %s --username %s --pin %s'
                % (self.k, k2, self.domain, self.username, self.pin)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, self.password]))

    def test_find_multiple_keyfiles_multiple_results(self):
        k2 = os.path.join(self.d.name, 'keyfile2')
        d2 = os.path.join(self.d.name, 'database2')
        cli.main(('init %s %s' % (k2, d2)).split(' '))
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (k2, self.domain + '2', self.username, self.pin, self.password)).split(' '))
        results = cli.main(
            ('find %s %s --domain %s --username %s --pin %s'
                % (self.k, k2, self.domain, self.username, self.pin)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, '', self.domain + '2', self.username]))

    def test_find_single_result_no_pin(self):
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        results = cli.main(
            ('find %s --domain %s --username %s'
                % (self.k, self.domain, self.username)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, '********']))

    def test_find_fuzzy_match(self):
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        results = cli.main(
            ('find %s --domain %s --username %s --pin %s'
                % (self.k, self.domain[0:2], self.username, self.pin)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, self.password]))

    def test_find_only_domain(self):
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        results = cli.main(
            ('find %s --domain %s --pin %s'
                % (self.k, self.domain, self.pin)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, self.password]))

    def test_find_only_username(self):
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        results = cli.main(
            ('find %s --username %s --pin %s'
                % (self.k, self.username, self.pin)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, self.password]))

    def test_update_defaults(self):
        results1 = cli.main(
            ('add %s --domain %s --username %s --pin %s'
                % (self.k, self.domain, self.username, self.pin)).split(' '))
        results2 = cli.main(
            ('update %s --domain %s --username %s --pin %s'
                % (self.k, self.domain, self.username, self.pin)).split(' '))
        with Database(self.keyfile) as d:
            c = d.find(domain=self.domain, username=self.username)[0]
        c.unlock(self.pin)
        print c
        self.assertEqual(results2, '\n'.join([c.domain, c.username, c.plainpassword]))
        self.assertNotEqual(results1, results2)

    def test_update_override(self):
        results1 = cli.main(
            ('add %s --domain %s --username %s --pin %s --length %d --characters %s'
                % (self.k, self.domain, self.username, self.pin, self.length, self.characters)).split(' '))
        results2 = cli.main(
            ('update %s --domain %s --username %s --pin %s --length %d --characters %s'
                % (self.k, self.domain, self.username, self.pin, self.length, self.characters)).split(' '))
        parts = results2.split('\n')
        self.assertEqual(self.length, len(parts[2]))
        for c in parts[2]:
            self.assertIn(c, self.characters)
        self.assertNotEqual(results1, results2)

    def test_update_provide_password(self):
        results1 = cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        results2 = cli.main(
            ('update %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password + '2')).split(' '))
        parts = results2.split('\n')
        self.assertEqual(self.password + '2', parts[2])
        self.assertNotEqual(results1, results2)

    def test_delete(self):
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        cli.main(
            ('delete %s --domain %s --username %s'
                % (self.k, self.domain, self.username)).split(' '))
        results = cli.main(
            ('find %s --domain %s --username %s --pin %s'
                % (self.k, self.domain, self.username, self.pin)).split(' '))
        self.assertEqual(results, '')

    def test_delete_not_fuzzy(self):
        cli.main(
            ('add %s --domain %s --username %s --pin %s --password %s'
                % (self.k, self.domain, self.username, self.pin, self.password)).split(' '))
        cli.main(
            ('delete %s --domain %s --username %s'
                % (self.k, self.domain[0:2], self.username)).split(' '))
        results = cli.main(
            ('find %s --domain %s --username %s --pin %s'
                % (self.k, self.domain, self.username, self.pin)).split(' '))
        self.assertEqual(results, '\n'.join([self.domain, self.username, self.password]))
