#! /bin/python

import os
import sys
import argparse

UTILS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "utils")
sys.path.append(UTILS_PATH)
import core

def password(database, pin, domain, username):
    print "Finding password"
    allresults = core.password(database, pin, domain, username)
    if not allresults:
        print "    -- none found --"
    elif isinstance(allresults, tuple):
        print "      Domain: %s" % allresults[0]
        print "    Username: %s" % allresults[1]
        print "    Password: %s" % allresults[2]
    else:
        print "    Did you mean one of these:"
        domains = {}
        for result in allresults:
            if result[0] in domains:
                domains[result[0]].append(result[1])
            else:
                domains[result[0]] = [result[1]]
        for key in domains:
            print "        %s" % key
            for username in domains[key]:
                print "            %s" % username

def users(database, domain):
    print "Finding domain matches"
    allresults = core.users(database, domain)
    if len(allresults) == 0:
        print "    -- none found --"
    else:
        domains = {}
        for result in allresults:
            if result[0] in domains:
                domains[result[0]].append(result[1])
            else:
                domains[result[0]] = [result[1]]
        for key in domains:
            print key
            for username in domains[key]:
                print "    %s" % username

def domains(database):
    print "Listing all domains"
    allresults = core.domains(database)
    if len(allresults) == 0:
        print "    -- none found --"
    else:
        for domain in allresults:
            print "    %s" % domain

def parseArgs(args):
    parser = argparse.ArgumentParser(description = 'pinscher - Password manager from the terminal')
    parser.add_argument("--domain", action = "store", default = None, help = "The domain these credentials are for")
    parser.add_argument("--username", action = "store", default = None, help = "The username")
    parser.add_argument("--password", action = "store", default = None, help = "The password")
    parser.add_argument("--new", action = "store_true", default = False, help = "Generate a new password")
    parser.add_argument("--pin", action = "store", default = None, help = "The PIN used to lock/unlock the password")
    parser.add_argument("--database", action = "store", help = "The pinscher database to look in")
    return parser.parse_args(args)

def main(args):
    args = parseArgs(args)
    if bool(args.pin) and (args.new != bool(args.password)) and bool(args.username) and bool(args.domain):
        if args.new:
            args.password = generate(10)
        add(args.database, args.pin, args.domain, args.username, args.password)
    elif bool(args.pin) and not args.new and not bool(args.password) and bool(args.username) and bool(args.domain):
        password(args.database, args.pin, args.domain, args.username)
    elif not bool(args.pin) and not args.new and not bool(args.password) and not bool(args.username) and bool(args.domain):
        users(args.database, args.domain)
    elif not bool(args.pin) and not args.new and not bool(args.password) and not bool(args.username) and not bool(args.domain):
        domains(args.database)
    else:
        print "You have provided an incorrect combination of arguments"

if __name__ == "__main__":
    main(sys.argv[1:])