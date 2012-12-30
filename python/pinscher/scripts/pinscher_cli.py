#! python

import sys
import argparse
from pinscher import pinscher as core


def delete(database, keyfile, pin, domain, username, password):
    core.delete(database, keyfile, pin, domain, username, password)


def add(database, keyfile, pin, domain, username, password):
    allresults = core.get(database, keyfile, pin, domain, username)
    if len(allresults) == 1:
        core.update(database, keyfile, pin, domain, username, password)
    else:
        core.insert(database, keyfile, pin, domain, username, password)


def password(database, keyfile, pin, domain, username):
    allresults = core.get(database, keyfile, pin, domain, username)
    display = []
    if len(allresults) == 1:
        display.append("  Domain: %s" % allresults[0][0])
        display.append("Username: %s" % allresults[0][1])
        display.append("Password: %s" % allresults[0][2])
    else:
        for (domain, username, password) in allresults:
            display.append("%s: %s" % (domain, username))
    return '\n'.join(display)


def users(database, keyfile, domain):
    allresults = core.get(database, keyfile, domain)
    display = []
    for (domain, username, password) in allresults:
        display.append("%s: %s" % (domain, username))
    return '\n'.join(display)


def domains(database, keyfile):
    allresults = core.get(database, keyfile)
    display = []
    for domain in set([r[0] for r in allresults]):
        display.append(domain)
    return '\n'.join(display)


def parseArgs(args):
    parser = argparse.ArgumentParser(description="pinscher - Password manager from the terminal")
    parser.add_argument("database", action="store", help="The pinscher database to look in")
    parser.add_argument("keyfile", action="store", help="The keyfile used to lock the database")
    parser.add_argument("--domain", action="store", help="The domain to assign the credentials to")
    parser.add_argument("--username", action="store", help="The username")
    parser.add_argument("--pin", action="store", help="The PIN used to lock the passwords")
    parser.add_argument("--delete", action="store_true", default=False, help="Flag to indicate that this record should be deleted")
    pass_or_new = parser.add_mutually_exclusive_group(required=False)
    pass_or_new.add_argument("--password", action="store", default=None, help="The new password")
    pass_or_new.add_argument("--new", action="store", default=10, help="Generate a new random password")

    return parser.parse_args(args)


def go(args):
    args = parseArgs(args)
    if args.domain:
        if args.username:
            if args.pin:
                if args.password and args.delete:
                    delete(args.database, args.keyfile, args.pin, args.domain, args.username, args.password)
                if args.new or args.password:
                    if args.new:
                        args.password = core.generate(args.new)
                    add(args.database, args.keyfile, args.pin, args.domain, args.username, args.password)
                else:
                    password(args.database, args.keyfile, args.pin, args.domain, args.username)
            else:
                print "Need PIN to unlock database"
        else:
            users(args.database, args.keyfile, args.domain)
    else:
        domains(args.database, args.keyfile)


def main():
    args = sys.argv[1:]
    result = go(args)
    print result

if __name__ == "__main__":
    main()
