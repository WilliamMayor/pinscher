#! /bin/python

import os
import sys
import argparse
import subprocess

import core

def add(database, pin, domain, username, password):
    allresults = core.password(database, pin, domain, username)
    p = subprocess.Popen(["pbcopy"], stdin = subprocess.PIPE)
    p.stdin.write(password)
    if isinstance(allresults, tuple):
        core.update(database, pin, domain, username, password)
        print "Updated password, copied to clipboard"
    else:
        core.insert(database, pin, domain, username, password)
        print "Added password, copied to clipboard"

def password(database, pin, domain, username):
    allresults = core.password(database, pin, domain, username)
    if isinstance(allresults, tuple):
        p = subprocess.Popen(["pbcopy"], stdin = subprocess.PIPE)
        p.stdin.write(allresults[2])
        print "Found password, copied to clipboard"
    else:
        print "Found multiple matches:"
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

def users(database, domain):
    print "Usernames:"
    allresults = core.users(database, domain)
    if len(allresults) == 0:
        print "-- none found --"
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
    print "Domains:"
    allresults = core.domains(database)
    if len(allresults) == 0:
        print "-- none found --"
    else:
        for domain in allresults:
            print domain

def pin(keyfile):
    with open(keyfile, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "pin=" in line:
                return line.replace("pin=", "").strip()

def parseArgs(argv):
    args = {}
    args['database'] = argv[0]
    args['pin'] = pin(argv[1])
    try:
        args['domain'] = argv[2]
        args['username'] = argv[3]
        args['password'] = argv[4]
    except IndexError:
        pass
    return args

def main(args):
    args = parseArgs(args)
    if 'domain' in args:
        if 'username' in args:
            if 'password' in args:
                if args['password'] == 'new':
                    args['password'] = core.generate(10)
                add(args['database'], args['pin'], args['domain'], args['username'], args['password'])
            else:
                password(args['database'], args['pin'], args['domain'], args['username'])
        else:
            if args['domain'] == 'list':
                domains(args['database'])
            else:
                users(args['database'], args['domain'])

if __name__ == "__main__":
    main(sys.argv[1:])