import socket

from Server import Server


class Database:

    @staticmethod
    def create(keyfile):
        Server.db_create(keyfile)

    def __init__(self, keyfile):
        self.keyfile = keyfile

    def __enter__(self):
        self.c = Server.connect(self.keyfile)
        return self

    def __exit__(self, type, value, traceback):
        self.c.shutdown(socket.SHUT_RDWR)
        self.c.close()

    def add(self, credentials, pin):
        self.c.sendall(Server.prepare_message('add', credentials=credentials, pin=pin))
        action, result = Server.receive_message(self.c)
        return result['result']

    def update(self, credentials, pin):
        self.c.sendall(Server.prepare_message('update', credentials=credentials, pin=pin))
        action, result = Server.receive_message(self.c)
        return result['result']

    def find(self, domain='', username=''):
        self.c.sendall(Server.prepare_message('find', domain=domain, username=username))
        action, result = Server.receive_message(self.c)
        return result['result']

    def delete(self, credentials):
        self.c.sendall(Server.prepare_message('delete', credentials=credentials))
        action, result = Server.receive_message(self.c)
        return result['result']

if __name__ == '__main__':
    from Keyfile import Keyfile
    from Credentials import Credentials
    k = Keyfile.load('/Users/william/Desktop/test.kf')
    with Database(k) as d:
        d.add(Credentials('domain1', 'username1', plainpassword='password1'), 1234)
        d.add(Credentials('domain2', 'username2', plainpassword='password2'), 1234)
        d.update(Credentials('domain2', 'username2', plainpassword='better password'), 1234)
    with Database(k) as d:
        print d.find(domain='d')
        d.delete(Credentials('domain1', 'username1'))
        d.delete(Credentials('domain2', 'username2'))
