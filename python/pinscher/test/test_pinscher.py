import unittest
import tempfile
from pinscher import pinscher as core
from find_schema import find_schema
from sqlite3 import IntegrityError


class TestPinscher(unittest.TestCase):

    def setUp(self):
        self.pin = 1234
        self.domain = 'domain'
        self.username = 'username'
        self.password = 'password'
        self.key, self.iv = core.Vault.make_key_iv(self.pin, self.domain, self.username)

        tempkeyfile = tempfile.NamedTemporaryFile()
        core.Vault.save_key_iv(tempkeyfile.name, self.key, self.iv)

        tempdb = tempfile.NamedTemporaryFile()
        with open(find_schema(), "r") as f:
            schema = f.read()
            with core.Database(tempdb.name, tempkeyfile.name) as cursor:
                cursor.executescript(schema)

        self.db = tempdb
        self.keyfile = tempkeyfile

    def tearDown(self):
        self.db.close()
        self.keyfile.close()

    def insert(self, pin=1234, domain='domain', username='username', password='password'):
        core.insert(self.db.name, self.keyfile.name, pin, domain, username, password)

    def update(self, pin=1234, domain='domain', username='username', password='password'):
        core.update(self.db.name, self.keyfile.name, pin, domain, username, password)

    def delete(self, pin=1234, domain='domain', username='username', password='password'):
        core.delete(self.db.name, self.keyfile.name, pin, domain, username, password)

    def get(self, pin=None, domain=None, username=None):
        return core.get(self.db.name, self.keyfile.name, pin=pin, domain=domain, username=username)

    def test_sqli(self):
        self.insert()
        self.get(username='1\'; DELETE FROM Credentials WHERE TRUE')
        self.assertEquals([(self.domain, self.username, self.password)], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_insert(self):
        self.insert()
        self.assertEquals([(self.domain, self.username, self.password)], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_insert_twice(self):
        self.insert()
        self.assertRaises(IntegrityError, self.insert)

    def test_update(self):
        self.insert()
        self.update(password='notpassword')
        self.assertEquals([(self.domain, self.username, 'notpassword')], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_update_nothing(self):
        self.update(password='notpassword')
        self.assertEquals([], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_delete_correct(self):
        self.insert()
        self.delete()
        self.assertEquals([], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_delete_bad_pin(self):
        self.insert()
        self.delete(pin=self.pin + 1)
        self.assertEquals([(self.domain, self.username, self.password)], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_delete_bad_password(self):
        self.insert()
        self.delete(password=self.password + 'a')
        self.assertEquals([(self.domain, self.username, self.password)], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_delete_partial_domain(self):
        self.insert()
        self.delete(domain=self.domain[0:3])
        self.assertEquals([(self.domain, self.username, self.password)], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_delete_partial_username(self):
        self.insert()
        self.delete(username=self.username[0:3])
        self.assertEquals([(self.domain, self.username, self.password)], self.get(domain=self.domain, username=self.username, pin=self.pin))

    def test_match_empty(self):
        self.assertItemsEqual([], self.get(domain='domain'))
        self.assertItemsEqual([], self.get(username='username'))
        self.assertItemsEqual([], self.get(domain='domain', username='username'))
        self.assertItemsEqual([], self.get(pin=1234, domain='domain', username='username'))

    def test_match_all(self):
        all = []
        for i in range(1, 10):
            u = str(i) + self.username
            d = self.domain + str(i)
            self.insert(domain=d, username=u)
            all.append((d, u, None))
        self.assertItemsEqual(all, core.get(self.db.name, self.keyfile.name))

    def test_match_exact_domain(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domain', username='otherusername')
        self.insert(domain='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ('domain', 'otherusername', None)], self.get(domain='domain'))

    def test_match_exact_domain_ignore_like(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domainclose', username='otherusername')
        self.insert(domain='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ], self.get(domain='domain'))

    def test_match_like_domain(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domainclose', username='otherusername')
        self.insert(domain='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ('domainclose', 'otherusername', None)], self.get(domain='dom'))

    def test_match_exact_domain_exact_username(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domain', username='otherusername')
        self.insert(domain='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ], self.get(domain='domain', username='username'))

    def test_match_exact_domain_like_username(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domain', username='otherusername')
        self.insert(domain='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ('domain', 'otherusername', None)], self.get(domain='domain', username='user'))

    def test_match_like_domain_like_username(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domainclose', username='otherusername')
        self.insert(domain='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ('domainclose', 'otherusername', None)], self.get(domain='dom', username='user'))

    def test_match_exact_username(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domain2', username='username')
        self.insert(domain='unrelated', username='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ('domain2', 'username', None)], self.get(username='username'))

    def test_match_exact_username_ignore_like(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domain2', username='otherusername')
        self.insert(domain='unrelated', username='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ], self.get(username='username'))

    def test_match_like_username(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domain2', username='otherusername')
        self.insert(domain='unrelated', username='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ('domain2', 'otherusername', None)], self.get(username='user'))

    def test_match_exact_username_like_domain(self):
        self.insert(domain='domain', username='username')
        self.insert(domain='domain2', username='username')
        self.insert(domain='unrelated', username='unrelated')
        self.assertItemsEqual([('domain', 'username', None), ('domain2', 'username', None)], self.get(domain='dom', username='username'))

    def test_pin_wrong(self):
        self.insert(domain='domain', username='username')
        get = self.get(domain='domain', username='username', pin=self.pin + 1)
        self.assertNotEqual(get[0][2], self.password)

    def test_get_password(self):
        self.insert(domain='domain', username='username')
        get = self.get(domain='domain', username='username', pin=self.pin)
        self.assertEqual(get[0][2], self.password)
