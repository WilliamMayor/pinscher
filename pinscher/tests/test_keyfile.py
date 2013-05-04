import unittest
import os
import pickle

from tempdir import TempDir

from .utilities import raises, not_raises

from pinscher.Keyfile import Keyfile as K


class TestCredentials(unittest.TestCase):

    key = '0b660492d98c54412d3d91818de5a2ae0b3110850a12010768b80fb277f55aa6'.decode('hex')
    iv = '9059d464b93397a2a98e8e1f00b596c6'.decode('hex')
    length = 5
    characters = 'abc'

    def setUp(self):
        self.d = TempDir()
        self.keyfile_path = os.path.join(self.d.name, 'keyfile')
        self.database_path = os.path.join(self.d.name, 'database')

    def tearDown(self):
        self.d.dissolve()

    @not_raises(AttributeError)
    def test_create_keyfile_generate(self):
        keyfile = K.create(
            self.keyfile_path,
            self.database_path)
        keyfile.key
        keyfile.iv
        keyfile.length
        keyfile.characters

    def test_create_keyfile_provided(self):
        keyfile = K.create(
            self.keyfile_path,
            self.database_path,
            key=self.key,
            iv=self.iv,
            length=self.length,
            characters=self.characters)
        self.assertEqual(keyfile.key, self.key)
        self.assertEqual(keyfile.iv, self.iv)
        self.assertEqual(keyfile.length, self.length)
        self.assertEqual(keyfile.characters, self.characters)

    @raises(AttributeError)
    def test_save_no_path(self):
        K.create(
            self.keyfile_path,
            self.database_path)
        k = pickle.load(open(self.keyfile_path, 'rb'))
        k.path

    @not_raises(AttributeError)
    def test_load_has_path(self):
        K.create(
            self.keyfile_path,
            self.database_path)
        k = K.load(self.keyfile_path)
        k.path

    @raises(IOError)
    def test_save_keyfile_cant_write_keyfile(self):
        K.create(
            '/nopermission',
            self.database_path)
