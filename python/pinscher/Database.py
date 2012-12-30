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
import sqlite3
from Vault import Vault


class Database():

    def __init__(self, path, keyfile):
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
