#! /bin/python

import os
import sys
import string
import hashlib
import sqlite3

LIBS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "libs")
sys.path.append(LIBS_PATH)
from aes import AESModeOfOperation

class Database():
    
    def __init__(self, path):
        dbcon = None
        self.path = path

    def __enter__(self):
        self.dbcon = sqlite3.connect(self.path)
        return self.dbcon.cursor()

    def __exit__(self, type, value, tb):
        if tb is None:
            self.dbcon.commit()
            self.dbcon.close()
            self.dbcon = None
        else:
            self.dbcon.rollback()
            self.dbcon.close()
            self.dbcon = None

def _key(pin, domain, username):
    """
    Generates the (key, iv) pair required to encrypt text.
    """
    return hashlib.sha256("%s%s%s" % (domain, pin, username)).hexdigest(), hashlib.sha256("%s%s%s" % (username, pin, domain)).hexdigest()

def _encrypt(key, iv, plaintext):
    moo = AESModeOfOperation()
    key = [int("%s%s" % (key[i], key[i+1]), 16) for i in range(0, len(key), 2)]
    iv = [int("%s%s" % (iv[i], iv[i+1]), 16) for i in range(0, len(iv), 2)]
    mode, orig_len, ciph = moo.encrypt(plaintext, moo.modeOfOperation["OFB"], key, moo.aes.keySize["SIZE_256"], iv)
    return ''.join(["%02x" % n for n in ciph])

def _decrypt(key, iv, ciphertext):
    moo = AESModeOfOperation()
    key = [int("%s%s" % (key[i], key[i+1]), 16) for i in range(0, len(key), 2)]
    iv = [int("%s%s" % (iv[i], iv[i+1]), 16) for i in range(0, len(iv), 2)]
    ciphertext = [int("%s%s" % (ciphertext[i], ciphertext[i+1]), 16) for i in range(0, len(ciphertext), 2)]
    return moo.decrypt(ciphertext, 0, moo.modeOfOperation["OFB"], key, moo.aes.keySize["SIZE_256"], iv)

def generate(size):
    return ''.join(random.choice(string.printable) for x in range(size))

def add(database, pin, domain, username, password):
    with Database(database) as cursor:
        query = "INSERT INTO Credentials(domain, username, password) VALUES(?,?,?)"
        key, iv = _key(pin, domain, username)
        cursor.execute(query, [domain, username, _encrypt(key, iv, password)])

def password(database, pin, domain, username):
    with Database(database) as cursor:
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
            key, iv = _key(pin, allresults[0][0], allresults[0][1])
            return (allresults[0][0], allresults[0][1], _decrypt(key, iv, allresults[0][2]))
        else:
            return [(r[0], r[1]) for r in allresults]

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
    