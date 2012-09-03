#! /bin/python

import os
import sys
import argparse

UTILS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "utils")
sys.path.append(UTILS_PATH)
import core

def add(database, pin, domain, username, password):
    allresults = core.password(database, pin, domain, username)
    if isinstance(allresults, tuple):
        print "Updating password"
        core.update(database, pin, domain, username, password)
    else:
        print "Adding password"
        core.insert(database, pin, domain, username, password)

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
            print "    %s" % key
            for username in domains[key]:
                print "        %s" % username

def domains(database):
    print "Listing all domains"
    allresults = core.domains(database)
    if len(allresults) == 0:
        print "    -- none found --"
    else:
        for domain in allresults:
            print "    %s" % domain

def parseArgs(args):
    parser = argparse.ArgumentParser(description = "pinscher - Password manager from the terminal")
    parser.add_argument("database", action = "store", help = "The pinscher database to look in")
    
    parser.add_argument("--domain", action = "store", help = "The domain to assign the credentials to")
    parser.add_argument("--username", action = "store", help = "The username")
    parser.add_argument("--pin", action = "store", help = "The PIN used to lock the password")
    pass_or_new = parser.add_mutually_exclusive_group(required=False)
    pass_or_new.add_argument("--password", action = "store", default = None, help = "The password")
    pass_or_new.add_argument("--new", action = "store_true", default = False, help = "Generate a random password")

    return parser.parse_args(args)

def main(args):
    args = parseArgs(args)
    if args.domain:
        if args.username:
            if args.pin:
                if args.new or args.password:
                    if args.new:
                        args.password = core.generate(10)
                    add(args.database, args.pin, args.domain, args.username, args.password)
                else:
                    password(args.database, args.pin, args.domain, args.username)
            else:
                print "Need PIN to unlock database"
        else:
            users(args.database, args.domain)
    else:
        domain(args.database)

if __name__ == "__main__":
    main(sys.argv[1:])