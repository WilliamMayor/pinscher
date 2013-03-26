import os
import apsw
from functools import wraps
from flask import Blueprint
from flask import jsonify
from flask import g
from flask import request
from Keyfile import Keyfile
from Database import Database, rowtrace
from Credentials import Credentials

config_path = os.path.join(os.getenv("HOME"), '.pinscher', 'config.db')
api = Blueprint('api', __name__)
valid_urls = [
    '/',
    '/keyfiles/',
    '/keyfiles/<keyfile>/',
    '/keyfiles/<keyfile>/domains/',
    '/keyfiles/<keyfile>/domains/<domain>/',
    '/keyfiles/<keyfile>/domains/<domain>/usernames/',
    '/keyfiles/<keyfile>/domains/<domain>/usernames/<username>/',
    '/keyfiles/<keyfile>/search/?domain=<domain>&username=<username>'
]


def query_db(db, query, args=()):
    cursor = db.cursor()
    cursor.setrowtrace(rowtrace)
    cursor.execute(query, args)
    return cursor.fetchall()


def check_keyfile(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        results = query_db(g.config, 'SELECT name, location, timeout FROM Keyfiles WHERE name=?', [kwargs['keyfile']])
        if len(results) == 0:
            return jsonify(error='No keyfile of that name: %s' % kwargs['keyfile']), 404
        else:
            g.keyfile = Keyfile(**results[0])
            return f(*args, **kwargs)
    return decorated_function


def check_domain(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with Database(g.keyfile) as cursor:
            query = 'SELECT domain, username, password FROM Credentials WHERE domain = ?'
            query_args = (kwargs['domain'],)
            cursor.execute(query, query_args)
            g.credentials = [Credentials(row['domain'], row['username'], row['password']) for row in cursor]
        if len(g.credentials) == 0:
            return jsonify(error='No domain of that name: %s' % kwargs['domain']), 404
        else:
            return f(*args, **kwargs)
    return decorated_function


def check_username(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with Database(g.keyfile) as cursor:
            query = 'SELECT domain, username, password FROM Credentials WHERE domain = ? AND username = ?'
            query_args = (kwargs['domain'], kwargs['username'],)
            cursor.execute(query, query_args)
            g.credentials = [Credentials(row['domain'], row['username'], row['password']) for row in cursor]
        if len(g.credentials) == 0:
            return jsonify(error='No details of domain %s with username %s' % (kwargs['domain'], kwargs['username'],)), 404
        else:
            return f(*args, **kwargs)
    return decorated_function


def check_pin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'pin' in request.args:
            return f(*args, **kwargs)
        else:
            return jsonify(error='No PIN provided'), 404
    return decorated_function


@api.before_request
def before_request():
    g.config = apsw.Connection(config_path)


@api.teardown_request
def teardown_request(exception):
    if hasattr(g, 'config'):
        g.config.close()


@api.route('/')
def index():
    return jsonify(valid_urls=valid_urls)


@api.route('/keyfiles/')
def all_keyfiles():
    return jsonify(keyfiles=[keyfile['name'] for keyfile in query_db(g.config, 'SELECT name FROM Keyfiles')])


@api.route('/keyfiles/<keyfile>/')
@check_keyfile
def keyfile(keyfile):
    return jsonify(keyfile=g.keyfile.to_dict())


@api.route('/keyfiles/<keyfile>/domains/')
@check_keyfile
def domains(keyfile):
    with Database(g.keyfile) as cursor:
        query = 'SELECT DISTINCT domain FROM Credentials'
        cursor.execute(query)
        return jsonify(domains=[credentials['domain'] for credentials in cursor.fetchall()])


@api.route('/keyfiles/<keyfile>/domains/<domain>/')
@check_keyfile
@check_domain
def domain(keyfile, domain):
    return jsonify(domain=domain, usernames=[credentials.username for credentials in g.credentials])


@api.route('/keyfiles/<keyfile>/domains/<domain>/usernames/')
@check_keyfile
@check_domain
def usernames(keyfile, domain):
    return jsonify(usernames=[credentials.username for credentials in g.credentials])


@api.route('/keyfiles/<keyfile>/domains/<domain>/usernames/<username>/')
@check_keyfile
@check_username
@check_pin
def password(keyfile, domain, username):
    return jsonify(domain=domain, username=username, password=g.credentials[0].get_password(request.args['pin']))


def __search(keyfile, domain, username):
    with Database(keyfile) as cursor:
        query = 'SELECT DISTINCT domain, username, password FROM Credentials WHERE '
        where = []
        args = []
        if domain is not None:
            where += ['domain LIKE ("%" || ? || "%")']
            args += [domain]
        if username is not None:
            where += ['username LIKE ("%" || ? || "%")']
            args += [username]
        query += ' AND '.join(where)
        return [Credentials(row['domain'], row['username'], row['password']) for row in cursor.execute(query, args)]


@api.route('/keyfiles/<keyfile>/search/')
@check_keyfile
def search(keyfile):
    if 'domain' not in request.args and 'username' not in request.args:
        return jsonify(error='No search query, try ?domain=<domain>&username=<username>'), 400
    results = __search(g.keyfile, request.args.get('domain', None), request.args.get('username', None))
    if len(results) == 1 and 'pin' in request.args:
        password = results[0].get_password(request.args['pin'])
        return jsonify(results=[dict(domain=results[0].domain, username=results[0].username, password=password)])
    else:
        return jsonify(results=[dict(domain=r.domain, username=r.username) for r in results])


@api.route('/search/')
def global_search():
    if 'domain' not in request.args and 'username' not in request.args:
        return jsonify(error='No search query, try ?domain=<domain>&username=<username>'), 400
    results = set()
    keyfiles = [Keyfile(**keyfile) for keyfile in query_db(g.config, 'SELECT name, location, timeout FROM Keyfiles')]
    for keyfile in keyfiles:
        r = __search(keyfile, request.args.get('domain', None), request.args.get('username', None))
        for c in r:
            c.keyfile = keyfile.name
        results |= set(r)
    if len(results) == 1 and 'pin' in request.args:
        password = results[0].get_password(request.args['pin'])
        return jsonify(results=[dict(domain=results[0].domain, username=results[0].username, password=password)])
    else:
        return jsonify(results=[dict(keyfile=r.keyfile, domain=r.domain, username=r.username) for r in results])
