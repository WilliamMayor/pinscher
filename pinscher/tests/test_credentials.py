import unittest
import hashlib

from pinscher.Credentials import Credentials as C


class TestCredentials(unittest.TestCase):

    domain = 'domain'
    username = 'username'
    plainpassword = 'password'
    cipherpassword = '69e00ec7020a4d22'.decode('hex')
    pin = '1234'
    key = hashlib.sha256(domain + username + pin).digest()
    iv = 'a3206f4194d1d7a252a9fe24b7b063b9'.decode('hex')

    def test_unlock(self):
        c = C(self.domain, self.username, cipherpassword=self.cipherpassword, iv=self.iv)
        self.assertEqual(self.plainpassword, c.unlock(self.pin))

    def test_unlock_incorrect_pin(self):
        c = C(self.domain, self.username, cipherpassword=self.cipherpassword, iv=self.iv)
        password = c.unlock('1111')
        self.assertNotEqual(password, self.plainpassword)

    def test_lock(self):
        c1 = C(self.domain, self.username, plainpassword=self.plainpassword)
        cipherpassword, iv = c1.lock(self.pin)
        c2 = C(self.domain, self.username, cipherpassword=cipherpassword, iv=iv)
        self.assertEqual(self.plainpassword, c2.unlock(self.pin))

    def test_eq(self):
        self.assertEqual(C('d', 'u'), C('d', 'u'))
        self.assertEqual(C('d', 'u', plainpassword='p'), C('d', 'u', plainpassword='p'))
        self.assertEqual(C('d', 'u', cipherpassword=self.cipherpassword, iv=self.iv), C('d', 'u', cipherpassword=self.cipherpassword, iv=self.iv))
        self.assertEqual(C('d', 'u'), C('d', 'u', plainpassword='p'))
        self.assertEqual(C('d', 'u'), C('d', 'u', cipherpassword=self.cipherpassword, iv=self.iv))

        self.assertNotEqual(C('d', 'u'), C('d', 'v'))
        self.assertNotEqual(C('d', 'u'), C('e', 'u'))
        self.assertNotEqual(C('d', 'u'), C('e', 'v'))
        self.assertNotEqual(C('d', 'u', cipherpassword=self.cipherpassword, iv=self.iv), C('d', 'u', cipherpassword=self.cipherpassword, iv='b3206f4194d1d7a252a9fe24b7b063ba'.decode('hex')))
