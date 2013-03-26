"""
    Vault. Class used for encrpytion methods
    Copyright (C) 2012  William Mayor

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    To contact the author please email: mail@williammayor.co.uk
"""
import hashlib
from Crypto.Cipher import AES


class Vault():

    @staticmethod
    def get_key_iv(keyfile):
        with open(keyfile, 'rb') as f:
            return [s.decode('hex') for s in f.read().split('\n', 1)]

    @staticmethod
    def save_key_iv(keyfile, key, iv):
        with open(keyfile, 'wb') as f:
            f.write("%s\n" % key.encode('hex'))
            f.write(iv.encode('hex'))

    @staticmethod
    def make_key_iv(pin, domain, username):
        """
        Generates the (key, iv) pair required to encrypt text.
        """
        return hashlib.sha256("%s%s%s" % (domain, pin, username)).digest(), hashlib.md5("%s%s%s" % (username, pin, domain)).digest()

    @staticmethod
    def encrypt(key, iv, plaintext):
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        if len(plaintext) % 16 != 0:
            plaintext += ' ' * (16 - len(plaintext) % 16)
        return encryptor.encrypt(plaintext).encode('hex')

    @staticmethod
    def decrypt(key, iv, ciphertext):
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        return encryptor.decrypt(ciphertext.decode('hex')).strip()
