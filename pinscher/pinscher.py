"""
    pinscher. The core functions for interacting with pinscher password files.
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
import string
import random
from Database import Database
from Vault import Vault


def generate(size=10):
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


def get(database, keyfile, pin=None, domain=None, username=None):
    if domain and username and pin:
        return _password(database, keyfile, pin, domain, username)
    return _match(database, keyfile, domain, username)


def _match(database, keyfile, domain=None, username=None):
    with Database(database, keyfile) as cursor:
        query_start = "SELECT domain, username FROM Credentials"
        queries = []
        if domain:
            if username:
                queries.append(("".join([query_start, " WHERE domain = ? AND username = ?"]), [domain, username]))
                queries.append(("".join([query_start, " WHERE domain = ? AND username LIKE ('%' || ? || '%')"]), [domain, username]))
                queries.append(("".join([query_start, " WHERE domain LIKE ('%' || ? || '%') AND username LIKE ('%' || ? || '%')"]), [domain, username]))
            else:
                queries.append(("".join([query_start, " WHERE domain = ?"]), [domain, ]))
                queries.append(("".join([query_start, " WHERE domain LIKE ('%' || ? || '%')"]), [domain, ]))
        else:
            if username:
                queries.append(("".join([query_start, " WHERE username = ?"]), [username, ]))
                queries.append(("".join([query_start, " WHERE username LIKE ('%' || ? || '%')"]), [username, ]))
            else:
                queries.append((query_start, []))
        for (query, params) in queries:
            cursor.execute(query, params)
            allresults = cursor.fetchall()
            if len(allresults) > 0:
                break
        return [(r[0], r[1], None) for r in allresults]


def _password(database, keyfile, pin, domain, username):
    match = _match(database, keyfile, domain, username)
    if len(match) == 1:
        with Database(database, keyfile) as cursor:
            query = "SELECT password FROM Credentials WHERE domain = ? AND username = ?"
            cursor.execute(query, [match[0][0], match[0][1]])
            allresults = cursor.fetchall()
            if len(allresults) == 1:
                key, iv = Vault.make_key_iv(pin, match[0][0], match[0][1])
                return [(match[0][0], match[0][1], Vault.decrypt(key, iv, allresults[0][0]))]
            match = allresults
    return match
