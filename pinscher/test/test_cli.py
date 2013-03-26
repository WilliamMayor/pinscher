import unittest
import tempfile
from pinscher import pinscher as core
from find_schema import find_schema
from pinscher.scripts import pinscher_cli as cli


class TestCli(unittest.TestCase):

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

    def args(self, domain=None, username=None, pin=None, delete=False, password=None, new=None):
        args = [self.db.name, self.keyfile.name]
        if domain:
            args.append("--domain")
            args.append(domain)
        if username:
            args.append("--username")
            args.append(username)
        if pin:
            args.append("--pin")
            args.append(str(pin))
        if delete:
            args.append("--delete")
        if password:
            args.append("--password")
            args.append(password)
        if new:
            args.append("--new")
            args.append(str(new))
        return args

    def test_delete(self):
        args = self.args(domain='d', username='u', pin=1234, password='p')
        cli.go(args)
        args = self.args(domain='d', username='u', pin=1234)
        details = cli.go(args)
        args = self.args(domain='d', username='u', pin=1234, password='p', delete=True)
        cli.go(args)
        args = self.args(domain='d', username='u', pin=1234)
        nodetails = cli.go(args)
        self.assertNotEqual(details, nodetails)

    def test_add_new(self):
        args = self.args(domain='d', username='u', pin=1234, password='p')
        result = cli.go(args)
        self.assertIsNone(result)
        args = self.args(domain='d', username='u', pin=1234)
        details = cli.go(args)
        self.assertEqual('  Domain: d\nUsername: u\nPassword: p', details)

    def test_add_update(self):
        pass

    def test_password_exact(self):
        pass

    def test_password_multiple(self):
        pass

    def test_users(self):
        pass

    def test_domains(self):
        pass
