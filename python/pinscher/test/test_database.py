import unittest
import tempfile
from pinscher import pinscher as core
from find_schema import find_schema


class TestDatabase(unittest.TestCase):

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

    def test_load_blank_file(self):
        with tempfile.NamedTemporaryFile() as tempkeyfile:
            core.Vault.save_key_iv(tempkeyfile.name, self.key, self.iv)
            with tempfile.NamedTemporaryFile() as tempdb:
                with core.Database(tempdb.name, tempkeyfile.name):
                    #loaded from blank file
                    pass

    def test_load_empty_database(self):
        with core.Database(self.db.name, self.keyfile.name):
            #loaded from minimal file (encrypted but empty)
            pass

    def test_load_save(self):
        with core.Database(self.db.name, self.keyfile.name) as cursor:
            query = "INSERT INTO Credentials(domain, username, password) VALUES(?,?,?)"
            cursor.execute(query, [self.domain, self.username, self.password])
        with core.Database(self.db.name, self.keyfile.name) as cursor:
            query = "SELECT domain, username, password FROM Credentials WHERE domain = ? AND username = ?"
            cursor.execute(query, [self.domain, self.username])
            result = cursor.fetchall()[0]
            self.assertEqual(result, (self.domain, self.username, self.password))
