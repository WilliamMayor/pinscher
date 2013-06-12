import unittest
import os
import hashlib
import sqlite3

from tempdir import TempDir
from Crypto import Random

from .utilities import raises

from pinscher.Keyfile import Keyfile as K
from pinscher.Database import Database as D
from pinscher.Credentials import Credentials as C
import pinscher.Database


class TestDatabase(unittest.TestCase):

    domain = 'domain'
    username = 'username'
    plainpassword = 'password'
    cipherpassword = '69e00ec7020a4d22'.decode('hex')
    pin = '1234'
    key = hashlib.sha256(domain + username + pin).digest()
    iv = 'a3206f4194d1d7a252a9fe24b7b063b9'.decode('hex')

    def setUp(self):
        pinscher.Database.Timeout.WAIT = 1
        self.d = TempDir()
        self.keyfile_path = os.path.join(self.d.name, 'keyfile')
        self.database_path = os.path.join(self.d.name, 'database')
        self.keyfile = K.create(
            self.keyfile_path,
            self.database_path)
        D.create(self.keyfile)

    def tearDown(self):
        self.d.dissolve()

    @raises(IOError)
    def test_create_database_exists(self):
        D.create(self.keyfile)

    @raises(AttributeError)
    def test_enter_missing_key(self):
        del self.keyfile.key
        with D(self.keyfile):
            pass

    @raises(ValueError)
    def test_enter_invalid_key(self):
        self.keyfile.key = 'not a key'
        with D(self.keyfile):
            pass

    @raises(ValueError)
    def test_enter_incorrect_key(self):
        self.keyfile.key = '1b660492d98c54412d3d91818de5a2ae0b3110850a12010768b80fb277f55aa5'.decode('hex')
        with D(self.keyfile):
            pass

    @raises(AttributeError)
    def test_enter_missing_iv(self):
        del self.keyfile.iv
        with D(self.keyfile):
            pass

    @raises(ValueError)
    def test_enter_invalid_iv(self):
        self.keyfile.iv = 'not an iv'
        with D(self.keyfile):
            pass

    @raises(ValueError)
    def test_enter_incorrect_iv(self):
        self.keyfile.iv = 'a059d464b93397a2a98e8e1f00b596c7'.decode('hex')
        with D(self.keyfile):
            pass

    @raises(AttributeError)
    def test_enter_missing_path(self):
        del self.keyfile.database_path
        with D(self.keyfile):
            pass

    @raises(IOError)
    def test_enter_unreadable_path(self):
        self.keyfile.database_path = '/nopermission'
        with D(self.keyfile):
            pass

    @raises(ValueError)
    def test_enter_not_a_database_path(self):
        self.keyfile.database_path = os.path.join(self.d.name, 'database')
        with open(self.keyfile.database_path, 'wb') as f:
            f.write(Random.new().read(10))
        with D(self.keyfile):
            pass

    def test_exit_saves_changes(self):
        c = C(self.domain, self.username, cipherpassword=self.cipherpassword, iv=self.iv)
        with D(self.keyfile) as d:
            d.add(c, self.pin)
        with D(self.keyfile) as d:
            self.assertEqual(
                [c],
                d.find(self.domain, self.username))

    def test_add(self):
        c1 = C(self.domain, self.username, cipherpassword=self.cipherpassword, iv=self.iv)
        with D(self.keyfile) as d:
            d.add(c1, self.pin)
            c2 = d.find(self.domain, self.username)[0]
            print c1
            print c2
            self.assertEqual(self.plainpassword, c2.unlock(self.pin))

    @raises(sqlite3.IntegrityError)
    def test_add_domain_username_exists(self):
        c = C(self.domain, self.username, cipherpassword=self.cipherpassword, iv=self.iv)
        with D(self.keyfile) as d:
            d.add(c, self.pin)
            d.add(c, self.pin)

    def test_find_none(self):
        with D(self.keyfile) as d:
            self.assertEqual([], d.find())

    def test_find_domain(self):
        c1 = C('d', 'u', plainpassword='p')
        c2 = C('d', 'v', plainpassword='p')
        c3 = C('e', 'u', plainpassword='p')
        with D(self.keyfile) as d:
            d.add(c1, self.pin)
            d.add(c2, self.pin)
            d.add(c3, self.pin)
            results = d.find(domain='d')
            self.assertIn(c1, results)
            self.assertIn(c2, results)
            self.assertNotIn(c3, results)

    def test_find_username(self):
        c1 = C('d', 'u', plainpassword='p')
        c2 = C('d', 'v', plainpassword='p')
        c3 = C('e', 'u', plainpassword='p')
        with D(self.keyfile) as d:
            d.add(c1, self.pin)
            d.add(c2, self.pin)
            d.add(c3, self.pin)
            results = d.find(username='u')
            self.assertIn(c1, results)
            self.assertNotIn(c2, results)
            self.assertIn(c3, results)

    def test_find_fuzzy_start(self):
        c1 = C('domain', 'u', plainpassword='p')
        c2 = C('e', 'v', plainpassword='p')
        with D(self.keyfile) as d:
            d.add(c1, self.pin)
            d.add(c2, self.pin)
            results = d.find(domain='dom')
            self.assertIn(c1, results)
            self.assertNotIn(c2, results)

    def test_find_fuzzy_middle(self):
        c1 = C('domain', 'u', plainpassword='p')
        c2 = C('e', 'v', plainpassword='p')
        with D(self.keyfile) as d:
            d.add(c1, self.pin)
            d.add(c2, self.pin)
            results = d.find(domain='mai')
            self.assertIn(c1, results)
            self.assertNotIn(c2, results)

    def test_find_fuzzy_end(self):
        c1 = C('domain', 'u', plainpassword='p')
        c2 = C('e', 'v', plainpassword='p')
        with D(self.keyfile) as d:
            d.add(c1, self.pin)
            d.add(c2, self.pin)
            results = d.find(domain='ain')
            self.assertIn(c1, results)
            self.assertNotIn(c2, results)

    def test_update(self):
        c1 = C('domain', 'u', plainpassword='p')
        c2 = C('domain', 'u', plainpassword='q')
        with D(self.keyfile) as d:
            d.add(c1, self.pin)
            d.update(c2, self.pin)
            c3 = d.find(domain='domain')[0]
            self.assertEqual(c2.plainpassword, c3.unlock(self.pin))
            self.assertNotEqual(c1.plainpassword, c3.unlock(self.pin))

    def test_delete(self):
        c = C('domain', 'u', plainpassword='p')
        with D(self.keyfile) as d:
            d.add(c, self.pin)
            d.delete(c)
            self.assertEqual([], d.find(domain='domain'))
