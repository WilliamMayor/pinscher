#! /bin/python
"""
Imports passwords to pinscher from a pass_export.sh plaintext file
"""

import os, sys
import sqlite3
import argparse

LIBS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "terminal")
sys.path.append(LIBS_PATH)
import core

def parseArgs(args):
    parser = argparse.ArgumentParser(description = "pinscher-pass_import - Imports passwords to pinscher from a pass_export.sh plaintext file")
    parser.add_argument("--database", "-db", action = "store", dest = "dbpath", help = "The location of the database to initialise. Defaults to current working directory")
    parser.add_argument("--export", "-ex", action = "store", dest = "expath", help = "The location of the file containing the plaintext passwords, exported using pass_export.sh")
    parser.add_argument("--pin", action = "store", help = "The PIN used to lock the passwords")
    return parser.parse_args(args)

def main(args):
    args = parseArgs(args)
    with open(args.expath, "r") as f:
        for line in f.readlines():
            domain, username, password = line.split(" ")
            core.add(args.dbpath, args.pin, domain, username, password.strip("\n"))


if __name__ == "__main__":
    main(sys.argv[1:])
