"""
    Database. Class used to easily encapsulate the encrypted sqlite3 database.
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
import threading
import apsw
import StringIO as io
from Crypto.Cipher import AES

timer = None


def rowtrace(cursor, row):
    return {desc[0]: column for desc, column in zip(cursor.getdescription(), row)}


class Database():

    def __init__(self, keyfile):
        self.keyfile = keyfile

    def __enter__(self):
        self.connection = apsw.Connection(self.keyfile.db_uri, flags=apsw.SQLITE_OPEN_URI | apsw.SQLITE_OPEN_READWRITE | apsw.SQLITE_OPEN_CREATE)
        self.cursor = self.connection.cursor()
        tables = list(self.cursor.execute('SELECT name FROM sqlite_master WHERE type = "table" AND name = "Credentials"'))
        global timer
        if len(tables) == 0:
            self.load_database()
            timer = Timer(self.keyfile.timeout,
                          self.save_database,
                          apsw.Connection(self.keyfile.db_uri, flags=apsw.SQLITE_OPEN_URI | apsw.SQLITE_OPEN_READWRITE | apsw.SQLITE_OPEN_CREATE))
            timer.start()
        else:
            timer.reset()
        self.cursor.execute('BEGIN TRANSACTION')
        self.cursor.setrowtrace(rowtrace)
        return self.cursor

    def __exit__(self, type, value, traceback):
        if traceback is None:
            self.cursor.execute('COMMIT TRANSACTION')
        else:
            self.cursor.execute('ROLLBACK TRANSACTION')
        self.cursor.close()
        self.connection.close()
        self.connection = None

    def save_database(self, connection):
        cipher = AES.new(self.keyfile.key, AES.MODE_CFB, self.keyfile.iv)
        output = io.StringIO()
        shell = apsw.Shell(stdout=output, db=connection)
        shell.process_command(".dump")
        with open(self.keyfile.data_location, 'wb') as f:
            f.write(cipher.encrypt(output.getvalue().encode('utf-8')))
        connection.close()

    def load_database(self):
        connection = apsw.Connection(self.keyfile.db_uri, flags=apsw.SQLITE_OPEN_URI | apsw.SQLITE_OPEN_READWRITE | apsw.SQLITE_OPEN_CREATE)
        cursor = connection.cursor()
        cipher = AES.new(self.keyfile.key, AES.MODE_CFB, self.keyfile.iv)
        with open(self.keyfile.data_location, 'rb') as f:
            cursor.execute(cipher.decrypt(f.read()))
        connection.close()


class Timer(threading.Thread):
    """
    http://code.activestate.com/recipes/577407-resettable-timer-class-a-little-enhancement-from-p/
    """
    def __init__(self, interval, function, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()
        self.resetted = True

    def cancel(self):
        self.finished.set()

    def run(self):
        while self.resetted:
            self.resetted = False
            self.finished.wait(self.interval)
        if not self.finished.isSet():
            self.function(*self.args, **self.kwargs)
        self.finished.set()

    def reset(self, interval=None):
        if interval:
            self.interval = interval
        self.resetted = True
        self.finished.set()
        self.finished.clear()
