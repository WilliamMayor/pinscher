#! /usr/bin/python

import sys
import subprocess
import pinschercore as core


def _pbcopy(text):
    p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    p.stdin.write(text)


def add(database, keyfile, pin, domain, username, password):
    allresults = core.password(database, keyfile, pin, domain, username)
    _pbcopy(password)
    if len(allresults) == 1:
        core.update(database, keyfile, pin, domain, username, password)
        print "Updated password, copied to clipboard"
    else:
        core.insert(database, keyfile, pin, domain, username, password)
        print "Added password, copied to clipboard"


def password(database, keyfile, pin, domain, username):
    allresults = core.password(database, keyfile, pin, domain, username)
    if len(allresults) == 0:
        print "No matches found"
    elif len(allresults) == 1:
        _pbcopy(allresults[0][2])
        print "Found password, copied to clipboard"
    else:
        print "Found multiple matches:"
        domains = _to_dict(allresults)
        for key in domains:
            print "%s: %s" % (key, ', '.join(domains[key]))


def _to_dict(results):
    domains = {}
    for result in results:
        if result[0] in domains:
            domains[result[0]].append(result[1])
        else:
            domains[result[0]] = [result[1]]
    return domains


def users(database, keyfile, domain):
    print "Usernames:"
    allresults = core.users(database, keyfile, domain)
    if len(allresults) == 0:
        print "-- none found --"
    else:
        domains = _to_dict(allresults)
        for key in domains:
            print "%s: %s" % (key, ', '.join(domains[key]))


def domains(database, keyfile):
    print "Domains:"
    allresults = core.domains(database, keyfile)
    if len(allresults) == 0:
        print "-- none found --"
    else:
        for domain in allresults:
            print domain


def parseArgs(argv):
    args = {}
    args['database'] = argv[0]
    args['keyfile'] = argv[1]
    try:
        args['domain'] = argv[2]
        args['username'] = argv[3]
        args['pin'] = argv[4]
        args['password'] = argv[5]
    except IndexError:
        pass
    return args


def main(args):
    args = parseArgs(args)
    if 'domain' in args:
        if 'username' in args:
            if 'pin' not in args:
                print 'No PIN provided'
                return
            if 'password' in args:
                if args['password'] == 'new':
                    args['password'] = core.generate(10)
                add(args['database'], args['keyfile'], args['pin'], args['domain'], args['username'], args['password'])
            else:
                password(args['database'], args['keyfile'], args['pin'], args['domain'], args['username'])
        else:
            if args['domain'] == 'list':
                domains(args['database'], args['keyfile'])
            else:
                users(args['database'], args['keyfile'], args['domain'])

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:
        print e