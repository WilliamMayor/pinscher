import sqlite3
import os

import utilities
from .Credentials import Credentials

SCHEMA = """BEGIN TRANSACTION;
CREATE TABLE Credentials(
    domain TEXT,
    username TEXT,
    password TEXT,
    iv TEXT,
    PRIMARY KEY (domain, username)
);
CREATE INDEX credentials_domain_index ON Credentials(domain);
CREATE INDEX credentials_username_index ON Credentials(username);
COMMIT;
"""


class Database:

    @staticmethod
    def create(keyfile):
        connection = sqlite3.connect(':memory:')
        connection.executescript(SCHEMA)
        if os.path.isfile(keyfile.database_path):
            raise IOError('Database file already exsits')
        with open(keyfile.database_path, 'wb') as f:
            f.write(
                utilities.encrypt(
                    keyfile.key,
                    keyfile.iv,
                    '\n'.join(connection.iterdump())))

    def __init__(self, keyfile):
        self.keyfile = keyfile
        self.connection = sqlite3.connect(':memory:')
        with open(self.keyfile.database_path, 'rb') as f:
            try:
                self.connection.executescript(
                    utilities.decrypt(
                        self.keyfile.key,
                        self.keyfile.iv, f.read()))
            except sqlite3.OperationalError:
                raise ValueError('Could not decrypt database')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        with open(self.keyfile.database_path, 'wb') as f:
            f.write(
                utilities.encrypt(
                    self.keyfile.key,
                    self.keyfile.iv,
                    '\n'.join(self.connection.iterdump())))
        self.connection.close()

    def __execute__(self, query, args):
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
        self.__execute__(query, args)

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
        self.__execute__(query, args)

    def find(self, domain='', username=''):
        query = ''.join([
            'SELECT domain, username, password, iv ',
            'FROM Credentials ',
            'WHERE domain LIKE ("%" || ? || "%") ',
            'AND username LIKE ("%" || ? || "%")'])
        args = [
            domain,
            username]
        rows = self.__execute__(query, args)
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
        self.__execute__(query, args)
