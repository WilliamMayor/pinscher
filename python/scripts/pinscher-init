#! /bin/python
"""
Creates a new pinscher database with the correct schema but with no contents.
"""

import sys, os
import sqlite3
import argparse
import shutil
import hashlib
from pinscher import core

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pinscher.schema")
DATABASE_PATH = os.path.join(os.getcwd(),"pinscher.db")
KEYFILE_PATH = os.path.join(os.getcwd(),"pinscher.keyfile")

def initDB(dbpath, kfpath, scpath):
    with open(scpath, "r") as f:
        schema = f.read()
        with core.Database(dbpath, kfpath) as cursor:
            cursor.executescript(schema)

def parseArgs(args):
    parser = argparse.ArgumentParser(description = 'pinscher-init - Creates a new pinscher database with the correct schema but with no contents')
    parser.add_argument("--keyfile", "-k", action = "store", default = KEYFILE_PATH, dest = "kfpath", help = "The location of the keyfile to use to encrypt the database")
    parser.add_argument("--schema", "-s", action = "store", default = SCHEMA_PATH, dest = "scpath", help = "The location of the pinscher schema file. Defaults to pinscher root directory")
    parser.add_argument("--database", "-db", action = "store", default = DATABASE_PATH, dest = "dbpath", help = "The location of the database to initialise. Defaults to current working directory")
    return parser.parse_args(args)

def makeDBFile(dbpath):
    with file(dbpath, 'a'):
        os.utime(dbpath, None)

def makeKeyfile(kfpath):
    try:
        key, iv = core.Vault.get_key_iv(kfpath)
    except:
        key = hashlib.sha256(core.generate(32)).digest()
        iv = hashlib.md5(core.generate(16)).digest()
        core.Vault.save_key_iv(kfpath, key, iv)

def main(args):
    args = parseArgs(args)
    makeDBFile(args.dbpath)
    makeKeyfile(args.kfpath)
    initDB(args.dbpath, args.kfpath, args.scpath)


if __name__ == "__main__":
    main(sys.argv[1:])
