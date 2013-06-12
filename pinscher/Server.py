import os
import pickle
import sqlite3
import socket
import hashlib
import threading
import time

from pkg_resources import resource_string

import utilities

from Credentials import Credentials


class Server():

    DELIMETER = 'p'

    @staticmethod
    def db_create(keyfile):
        connection = sqlite3.connect(':memory:')
        schema = resource_string(__name__, 'schema.sql')
        connection.executescript(schema)
        if os.path.isfile(keyfile.database_path):
            raise IOError('Database file already exsits')
        with open(keyfile.database_path, 'wb') as f:
            f.write(
                utilities.encrypt(
                    keyfile.key,
                    keyfile.iv,
                    '\n'.join(connection.iterdump())))

    @staticmethod
    def connect(keyfile):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(Server.get_address(keyfile))
        return s
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(Server.get_address(keyfile))
            return s
        except:
            server = Server(keyfile)
            pid = os.fork()
            if pid == 0:
                server.run()
                os._exit(0)
            else:
                s.connect(Server.get_address(keyfile))
                return s

    @staticmethod
    def get_address(keyfile):
        ext = hashlib.sha256(keyfile.path).digest().encode('hex')
        return '/tmp/pinscher.%s' % ext

    @staticmethod
    def prepare_message(action, **kwargs):
        message = ' '.join([action, pickle.dumps(kwargs)])
        return Server.DELIMETER.join([str(len(message)), message])

    @staticmethod
    def receive_message(connection):
        length = ''
        while True:
            chunk = connection.recv(1)
            if chunk == '':
                return None, None
            elif chunk != Server.DELIMETER:
                length += chunk
            else:
                message = connection.recv(int(length))
                parts = message.split(' ', 1)
                return parts[0], pickle.loads(parts[1])

    def __init__(self, keyfile):
        self.stop = False
        self.keyfile = keyfile
        self.address = Server.get_address(keyfile)
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.s.bind(self.address)
        except:
            os.remove(self.address)
            self.s.bind(self.address)
        self.s.listen(1)

    def run(self):
        self.db_connect()
        self.start_timeout()
        while not self.stop:
            connection, client_address = self.s.accept()
            self.converse(connection)
            connection.close()

    def converse(self, connection):
        while True:
            action, kwargs = Server.receive_message(connection)
            if action is None:
                return
            result = {
                'shutdown': self.shutdown,
                'add': self.add,
                'update': self.update,
                'find': self.find,
                'delete': self.delete,
            }[action](**kwargs)
            try:
                connection.sendall(
                    Server.prepare_message('result', result=result))
            except:
                pass

    def db_connect(self):
        self.db = sqlite3.connect(':memory:')
        with open(self.keyfile.database_path, 'rb') as f:
            try:
                self.db.executescript(
                    utilities.decrypt(
                        self.keyfile.key,
                        self.keyfile.iv,
                        f.read()))
            except sqlite3.OperationalError:
                raise ValueError('Could not decrypt database')

    def shutdown(self):
        with open(self.keyfile.database_path, 'wb') as f:
            f.write(
                utilities.encrypt(
                    self.keyfile.key,
                    self.keyfile.iv,
                    '\n'.join(self.db.iterdump())))
        self.db.close()
        self.s.close()
        os.remove(self.address)
        self.stop = True

    def start_timeout(self):
        t = Timeout(self.keyfile)
        t.start()

    def __execute__(self, query, args):
        cursor = self.db.cursor()
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
        return credentials

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
        return credentials

    def find(self, domain, username):
        query = ''.join([
            'SELECT domain, username, password, iv ',
            'FROM Credentials ',
            'WHERE domain LIKE ("%" || ? || "%") ',
            'AND username LIKE ("%" || ? || "%")'])
        args = [
            domain,
            username]
        rows = self.__execute__(query, args)
        results = []
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


class Timeout(threading.Thread):

    WAIT = 10

    def __init__(self, keyfile):
        super(Timeout, self).__init__()
        self.keyfile = keyfile

    def run(self):
        time.sleep(self.WAIT)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.connect(Server.get_address(self.keyfile))
            s.sendall(Server.prepare_message('shutdown'))
        except:
            pass
        s.close()

if __name__ == '__main__':
    time.sleep(10)
    with open('/Users/william/Desktop/Server.txt', 'a') as f:
        f.write('Slept for 10 seconds')

    exit()
    import sys
    from Keyfile import Keyfile

    try:
        keyfile = Keyfile.load(sys.argv[1])
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(Server.get_address(keyfile))
        s.shutdown(socket.SHUT_RDWR)
        s.close()
    except:
        server = Server(keyfile)
        server.run()
