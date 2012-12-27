#! /bin/python
"""
Encrypts the provided database and saves the results into the second.
"""

import sys, os
import sqlite3
import argparse
import shutil
from pinscher import core

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pinscher.schema")
DATABASE_PATH = os.path.join(os.getcwd(),"pinscher.db")

def copyDB(plain, cipher, keyfile, pin):
    dbcon = sqlite3.connect(plain)
    cursor = dbcon.cursor()
    query = "SELECT domain, username, password FROM Credentials"
    cursor.execute(query)
    for (domain, username, password) in cursor.fetchall():
        try:
            core.insert(cipher, keyfile, pin, domain, username, password)
        except Exception as e:
            print e
    cursor.close()

def parseArgs(args):
    parser = argparse.ArgumentParser(description = 'pinscher-decrypt - Populates a database with the unencrypted contents of another')
    parser.add_argument("--cipher", "-c", action = "store", help = "The encrypted database to save into")
    parser.add_argument("--pin", action = "store", help = "The PIN for the database")
    parser.add_argument("--keyfile", action = "store", help = "The keyfile for the database")
    parser.add_argument("--plain", "-p", action = "store", help = "The unencrypted database to use")
    return parser.parse_args(args)


def main(args):
    args = parseArgs(args)
    copyDB(args.plain, args.cipher, args.keyfile, args.pin)


if __name__ == "__main__":
    main(sys.argv[1:])
