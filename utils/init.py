#! /bin/python
"""
Creates a new pinscher database with the correct schema but with no contents.
"""

import sys, os
import sqlite3
import argparse
import shutil

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pinscher.schema")
DATABASE_PATH = os.path.join(os.getcwd(),"pinscher.db")

def initDB(dbpath, scpath):
    with open(scpath, "r") as f:
        schema = f.read()
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        cursor.executescript(schema)
        cursor.close()

def parseArgs(args):
    parser = argparse.ArgumentParser(description = 'pinscher-init - Creates a new pinscher database with the correct schema but with no contents')
    parser.add_argument("--backup", "-b", action = "store_true", default = False, help = "If a file with the given path already exists, make a backup. Defaults to off")
    parser.add_argument("--schema", "-s", action = "store", default = SCHEMA_PATH, dest = "scpath", help = "The location of the pinscher schema file. Defaults to pinscher root directory")
    parser.add_argument("--database", "-db", action = "store", default = DATABASE_PATH, dest = "dbpath", help = "The location of the database to initialise. Defaults to current working directory")
    return parser.parse_args(args)


def main(args):
    args = parseArgs(args)
    if os.path.isfile(args.dbpath):
        if args.backup:
            shutil.move(args.dbpath, "%s.bak" % args.dbpath)
        else:
            os.remove(args.dbpath)
    initDB(args.dbpath, args.scpath)


if __name__ == "__main__":
    main(sys.argv[1:])
