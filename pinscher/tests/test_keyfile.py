import tempfile
import pickle

from nose.tools import assert_equals, assert_is_not_none

from pinscher.Keyfile import Keyfile


def test_create_defaults():
    kf = tempfile.NamedTemporaryFile('wb')
    df = tempfile.NamedTemporaryFile('wb')
    with Keyfile(kf.name, database_path=df.name) as k:
        assert_equals(k['database_path'], df.name)
        assert_equals(k['characters'], Keyfile.CHARACTERS)
        assert_equals(k['length'], Keyfile.LENGTH)
        assert_is_not_none(k['key'])
        assert_is_not_none(k['iv'])


def test_create():
    kf = tempfile.NamedTemporaryFile('wb')
    df = tempfile.NamedTemporaryFile('wb')
    with Keyfile(kf.name,
                 database_path=df.name,
                 key='key',
                 iv='iv',
                 characters='abc', length=5) as k:
        assert_equals(k['database_path'], df.name)
        assert_equals(k['characters'], 'abc')
        assert_equals(k['length'], 5)
        assert_equals(k['key'], 'key')
        assert_equals(k['iv'], 'iv')


def test_pickled():
    kf = tempfile.NamedTemporaryFile('wb')
    df = tempfile.NamedTemporaryFile('wb')
    with Keyfile(kf.name, database_path=df.name) as k:
        orig = k
    with open(kf.name, 'rb') as fd:
        unpickled = pickle.load(fd)
    assert_equals(orig, unpickled)


def test_changes_saved():
    kf = tempfile.NamedTemporaryFile('wb')
    df = tempfile.NamedTemporaryFile('wb')
    with Keyfile(kf.name, database_path=df.name) as k:
        k['key'] = 'other key'
    with Keyfile(kf.name) as k:
        assert_equals(k['key'], 'other key')
