import unittest
import tempfile
from pinscher import pinscher as core
from find_schema import find_schema


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

    def test_insert(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, self.password)
        self.assertEquals([(self.domain, self.username, self.password)], core.get(self.db.name, self.keyfile.name, self.pin, self.domain, self.username))

    def test_update(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, self.password)
        core.update(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, 'notpassword')
        self.assertEquals([(self.domain, self.username, 'notpassword')], core.get(self.db.name, self.keyfile.name, self.pin, self.domain, self.username))

    def test_delete(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, self.password)
        core.delete(self.db.name, self.keyfile.name, self.pin, self.domain, self.username, self.password)
        self.assertEquals([], core.get(self.db.name, self.keyfile.name, self.pin, self.domain, self.username))

    def test_match_empty(self):
        self.assertItemsEqual([], core.get(self.db.name, self.keyfile.name, domain='domain'))
        self.assertItemsEqual([], core.get(self.db.name, self.keyfile.name, username='username'))
        self.assertItemsEqual([], core.get(self.db.name, self.keyfile.name, domain='domain', username='username'))
        self.assertItemsEqual([], core.get(self.db.name, self.keyfile.name, pin=1234, domain='domain', username='username'))

    def test_match_all(self):
        all = []
        for i in range(1, 10):
            core.insert(self.db.name, self.keyfile.name, self.pin, self.domain + str(i), str(i) + self.username, self.password)
            all.append((self.domain + str(i), str(i) + self.username, None))
        self.assertItemsEqual(all, core.get(self.db.name, self.keyfile.name))

    def test_match_exact_domain(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'otherusername', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', self.username, self.password)
        self.assertItemsEqual([('domain', 'username', None), ('domain', 'otherusername', None)], core.get(self.db.name, self.keyfile.name, domain='domain'))

    def test_match_exact_domain_ignore_like(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domainclose', 'otherusername', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', self.username, self.password)
        self.assertItemsEqual([('domain', 'username', None), ], core.get(self.db.name, self.keyfile.name, domain='domain'))

    def test_match_like_domain(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domainclose', 'otherusername', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', self.username, self.password)
        self.assertItemsEqual([('domain', 'username', None), ('domainclose', 'otherusername', None)], core.get(self.db.name, self.keyfile.name, domain='dom'))

    def test_match_exact_domain_exact_username(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'otherusername', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', self.username, self.password)
        self.assertItemsEqual([('domain', 'username', None), ], core.get(self.db.name, self.keyfile.name, domain='domain', username='username'))

    def test_match_exact_domain_like_username(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'otherusername', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', self.username, self.password)
        self.assertItemsEqual([('domain', 'username', None), ('domain', 'otherusername', None)], core.get(self.db.name, self.keyfile.name, domain='domain', username='user'))

    def test_match_like_domain_like_username(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domainclose', 'otherusername', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', self.username, self.password)
        self.assertItemsEqual([('domain', 'username', None), ('domainclose', 'otherusername', None)], core.get(self.db.name, self.keyfile.name, domain='dom', username='user'))

    def test_match_exact_username(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain2', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', 'unrelated', self.password)
        self.assertItemsEqual([('domain', 'username', None), ('domain2', 'username', None)], core.get(self.db.name, self.keyfile.name, username='username'))

    def test_match_exact_username_ignore_like(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain2', 'otherusername', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', 'unrelated', self.password)
        self.assertItemsEqual([('domain', 'username', None), ], core.get(self.db.name, self.keyfile.name, username='username'))

    def test_match_like_username(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain2', 'otherusername', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', 'unrelated', self.password)
        self.assertItemsEqual([('domain', 'username', None), ('domain2', 'otherusername', None)], core.get(self.db.name, self.keyfile.name, username='user'))

    def test_match_exact_username_like_domain(self):
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'domain2', 'username', self.password)
        core.insert(self.db.name, self.keyfile.name, self.pin, 'unrelated', 'unrelated', self.password)
        self.assertItemsEqual([('domain', 'username', None), ('domain2', 'username', None)], core.get(self.db.name, self.keyfile.name, domain='dom', username='username'))

    def test_pin_wrong(self):
        raise Exception("Not tested yet")
