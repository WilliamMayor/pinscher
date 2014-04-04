import sqlite3
import os

import pinscher.utilities as utilities
from pinscher.Secret import Secret

SCHEMA = """BEGIN TRANSACTION;
CREATE TABLE Secret(
    id INTEGER PRIMARY KEY,
    iv TEXT NOT NULL,
    secret TEXT NOT NULL
);
CREATE TABLE Tag(
    id INTEGER PRIMARY KEY,
    tag TEXT UNIQUE NOT NULL
);
CREATE TABLE SecretTag(
    secret INTEGER NOT NULL,
    tag INTEGER NOT NULL,
    FOREIGN KEY (secret) REFERENCES Secret(id),
    FOREIGN KEY (tag) REFERENCES Tag(id)
);
CREATE INDEX index_Tag_tag ON Tag(tag);
COMMIT;
"""


class Database:

    @staticmethod
    def create(keyfile):
        if os.path.isfile(keyfile.database_path):
            raise IOError('Database file already exsits')
        connection = sqlite3.connect(':memory:')
        connection.executescript(SCHEMA)
        with open(keyfile.database_path, 'wb') as fd:
            fd.write(
                utilities.encrypt(
                    keyfile.key,
                    keyfile.iv,
                    '\n'.join(connection.iterdump())))

    def __init__(self, keyfile):
        self.keyfile = keyfile
        self.connection = sqlite3.connect(':memory:')
        try:
            with open(self.keyfile.database_path, 'rb') as fd:
                cipher = fd.read()
            plain = utilities.decrypt(
                self.keyfile.key,
                self.keyfile.iv,
                cipher)
            self.connection.executescript(plain)
        except IOError:
            # TODO: This could led to losing the database
            # If there is an IOError that isn't caused by
            # the database file not existing
            self.connection.executescript(SCHEMA)
        except sqlite3.OperationalError:
            raise ValueError('Could not decrypt database')

    def save(self):
        with open(self.keyfile.database_path, 'wb') as fd:
            fd.write(
                utilities.encrypt(
                    self.keyfile.key,
                    self.keyfile.iv,
                    '\n'.join(self.connection.iterdump())))
        self.connection.close()

    def _execute(self, query, args):
        cursor = self.connection.cursor()
        results = list(cursor.execute(query, args))
        cursor.close()
        return results

    def add(self, credentials, pin):
        cipherpassword, iv = credentials.lock(pin)
        query = ''.join([
            'INSERT INTO ',
            'Credentials(domain, username, password, iv) ',
            'VALUES(?,?,?,?)'])
        args = [
            credentials.domain,
            credentials.username,
            cipherpassword.encode('hex'),
            iv.encode('hex')]
        self._execute(query, args)

    def update(self, credentials, pin):
        cipherpassword, iv = credentials.lock(pin)
        query = ''.join([
            'UPDATE Credentials ',
            'SET password=?, iv=? ',
            'WHERE domain=? ',
            'AND username=?'])
        args = [
            cipherpassword.encode('hex'),
            iv.encode('hex'),
            credentials.domain,
            credentials.username]
        self._execute(query, args)

    def find(self, domain='', username=''):
        query = ''.join([
            'SELECT domain, username, password, iv ',
            'FROM Credentials ',
            'WHERE domain LIKE ("%" || ? || "%") ',
            'AND username LIKE ("%" || ? || "%")'])
        args = [
            domain,
            username]
        rows = self._execute(query, args)
        results = map(
            lambda row: Credentials(
                domain=row[0],
                username=row[1],
                cipherpassword=row[2].decode('hex'),
                iv=row[3].decode('hex')),
            rows)
        return results

    def delete(self, credentials):
        query = ''.join([
            'DELETE FROM Credentials ',
            'WHERE domain=? ',
            'AND username=?'])
        args = [
            credentials.domain,
            credentials.username]
        self._execute(query, args)
