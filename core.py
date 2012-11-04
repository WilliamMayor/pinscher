#! /bin/python

import os
import sys
import string
import hashlib
import sqlite3
import random
from libs.Crypto.Cipher import AES

class Database():
    
    def __init__(self, path, keyfile):
        dbcon = None
        self.path = path
        self.key, self.iv = Vault.get_key_iv(keyfile)
        with open(path, 'rb') as f:
            self.ciphersql = f.read()

    def __enter__(self):
        self.dbcon = sqlite3.connect(":memory:")
        self.dbcon.executescript(Vault.decrypt(self.key, self.iv, self.ciphersql))
        return self.dbcon.cursor()

    def __exit__(self, type, value, traceback):
        if traceback is None:
            self.dbcon.commit()
        else:
            self.dbcon.rollback()
        lines = list(self.dbcon.iterdump())  
        with open(self.path, 'wb') as f:
                f.write(Vault.encrypt(self.key, self.iv, '\n'.join(lines)))
        self.dbcon.close()
        self.dbcon = None

class Vault():

    @staticmethod
    def get_key_iv(keyfile):
        with open(keyfile, 'rb') as f:
            return f.read().split('\n',1)

    @staticmethod
    def save_key_iv(keyfile, key, iv):
        with open(keyfile, 'wb') as f:
            f.write("%s\n" % key)
            f.write(iv)

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

def generate(size):
    return ''.join(random.choice(string.digits + string.letters + string.punctuation) for x in range(size))

def delete(database, keyfile, pin, domain, username, password):
    with Database(database, keyfile) as cursor:
        query = "DELETE FROM Credentials WHERE domain = ? AND username = ? AND password = ?"
        key, iv = Vault.make_key_iv(pin, domain, username)
        cursor.execute(query, [domain, username, Vault.encrypt(key, iv, password)])

def update(database, keyfile, pin, domain, username, password):
    with Database(database, keyfile) as cursor:
        query = "UPDATE Credentials SET password = ? WHERE domain = ? AND username = ?"
        key, iv = Vault.make_key_iv(pin, domain, username)
        cursor.execute(query, [Vault.encrypt(key, iv, password), domain, username])

def insert(database, keyfile, pin, domain, username, password):
    with Database(database, keyfile) as cursor:
        query = "INSERT INTO Credentials(domain, username, password) VALUES(?,?,?)"
        key, iv = Vault.make_key_iv(pin, domain, username)
        cursor.execute(query, [domain, username, Vault.encrypt(key, iv, password)])

def password(database, keyfile, pin, domain, username):
    with Database(database, keyfile) as cursor:
        query = "SELECT domain, username, password FROM Credentials WHERE domain = ? AND username = ?"
        cursor.execute(query, [domain, username])
        allresults = cursor.fetchall()
        if len(allresults) == 0:
            query = "SELECT domain, username, password FROM Credentials WHERE domain = ? AND username LIKE (? || '%')"
            cursor.execute(query, [domain, username])
            allresults = cursor.fetchall()
            if len(allresults) == 0:
                query = "SELECT domain, username, password FROM Credentials WHERE domain LIKE (? || '%') AND username LIKE (? || '%')"
                cursor.execute(query, [domain, username])
                allresults = cursor.fetchall()
        if len(allresults) == 1:
            key, iv = Vault.make_key_iv(pin, domain, username)
            return [(allresults[0][0], allresults[0][1], Vault.decrypt(key, iv, allresults[0][2]))]
        else:
            return [(r[0], r[1], None) for r in allresults]

def users(database, domain):
    with Database(database) as cursor:
        query = "SELECT domain, username FROM Credentials WHERE domain LIKE (? || '%')"
        cursor.execute(query, [domain])
        return cursor.fetchall()

def domains(database):
    with Database(database) as cursor:
        query = "SELECT DISTINCT domain FROM Credentials"
        cursor.execute(query)
        return [d[0] for d in cursor.fetchall()]

if __name__ == "__main__":
    # Let's run some tests.
    import tempfile

    key, iv = Vault.make_key_iv(1234,'domain','username')

    #vault saves and loads key iv
    with tempfile.NamedTemporaryFile() as tempf:
        Vault.save_key_iv(tempf.name, key, iv)
        assert [key, iv] == Vault.get_key_iv(tempf.name)

    #vault encrypts and decrypts
    key, iv = Vault.make_key_iv(1234,'domain','username')
    plaintext = 'test'
    ciphertext = Vault.encrypt(key, iv, plaintext)
    assert plaintext == Vault.decrypt(key, iv, ciphertext)

    #database loads saves and loads (test the initialising)
    with tempfile.NamedTemporaryFile() as tempkeyfile:
        Vault.save_key_iv(tempkeyfile.name, key, iv)
        with tempfile.NamedTemporaryFile() as tempdb:
            with Database(tempdb.name, tempkeyfile.name) as db:
                #loaded from blank file
                pass
            #closed and saved
            with Database(tempdb.name, tempkeyfile.name) as db:
                #loaded from minimal file
                pass
    
    # can insert into database
    with tempfile.NamedTemporaryFile() as tempkeyfile:
        Vault.save_key_iv(tempkeyfile.name, key, iv)
        with tempfile.NamedTemporaryFile() as tempdb:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pinscher.schema"), "r") as f:
                schema = f.read()
                with Database(tempdb.name, tempkeyfile.name) as cursor:
                    cursor.executescript(schema)
                insert(tempdb.name, tempkeyfile.name, 1234, 'domain', 'username', 'password')
                assert [('domain', 'username', 'password')] == password(tempdb.name, tempkeyfile.name, 1234, 'domain', 'username')

    # can update database records
    with tempfile.NamedTemporaryFile() as tempkeyfile:
        Vault.save_key_iv(tempkeyfile.name, key, iv)
        with tempfile.NamedTemporaryFile() as tempdb:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pinscher.schema"), "r") as f:
                schema = f.read()
                with Database(tempdb.name, tempkeyfile.name) as cursor:
                    cursor.executescript(schema)
                insert(tempdb.name, tempkeyfile.name, 1234, 'domain', 'username', 'password')
                update(tempdb.name, tempkeyfile.name, 1234, 'domain', 'username', 'notpassword')
                assert [('domain', 'username', 'notpassword')] == password(tempdb.name, tempkeyfile.name, 1234, 'domain', 'username')

    # can delete database records
    with tempfile.NamedTemporaryFile() as tempkeyfile:
        Vault.save_key_iv(tempkeyfile.name, key, iv)
        with tempfile.NamedTemporaryFile() as tempdb:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pinscher.schema"), "r") as f:
                schema = f.read()
                with Database(tempdb.name, tempkeyfile.name) as cursor:
                    cursor.executescript(schema)
                insert(tempdb.name, tempkeyfile.name, 1234, 'domain', 'username', 'password')
                delete(tempdb.name, tempkeyfile.name, 1234, 'domain', 'username', 'password')
                assert [] == password(tempdb.name, tempkeyfile.name, 1234, 'domain', 'username')