#! /bin/python
"""
Unencrypts the provided database and saves the results into the second.
"""

import sys, os
import sqlite3
import argparse
import shutil
from pinscher import core

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pinscher.schema")
DATABASE_PATH = os.path.join(os.getcwd(),"pinscher.db")

def copyDB(cipher, pin, plain):
    for domain in core.domains(cipher):
        for d, username in core.users(cipher, domain):
            d, u, password = core.password(cipher, pin, domain, username)
            try:
                with core.Database(plain) as cursor:
                    query = "INSERT INTO Credentials(domain, username, password) VALUES(?,?,?)"
                    cursor.execute(query, [domain, username, password])
            except Exception as e:
                print e
            print domain, username, password

def parseArgs(args):
    parser = argparse.ArgumentParser(description = 'pinscher-decrypt - Populates a database with the unencrypted contents of another')
    parser.add_argument("--cipher", "-c", action = "store", help = "The encrypted database to use")
    parser.add_argument("--pin", action = "store", help = "The PIN for the database")
    parser.add_argument("--plain", "-p", action = "store", help = "The unencrypted database to save into")
    return parser.parse_args(args)


def main(args):
    args = parseArgs(args)
    copyDB(args.cipher, args.pin, args.plain)


if __name__ == "__main__":
    main(sys.argv[1:])
