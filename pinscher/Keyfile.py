import string
import pickle
import os

import utilities


class Keyfile:

    LENGTH = 32
    CHARACTERS = string.digits + string.letters + string.punctuation + ' '

    @staticmethod
    def create(path, database_path, **kwargs):
        k = Keyfile()
        k.path = path
        k.database_path = database_path
        k.key = kwargs.get('key', utilities.generate_key())
        k.iv = kwargs.get('iv', utilities.generate_iv())
        k.length = kwargs.get('length', Keyfile.LENGTH)
        k.characters = kwargs.get('characters', Keyfile.CHARACTERS)
        k.save()
        return Keyfile.load(path)

    @staticmethod
    def load(path):
        k = pickle.load(open(path, 'rb'))
        k.path = path
        return k

    def __getstate__(self):
        _dict = self.__dict__.copy()
        del _dict['path']
        return _dict

    def __setstate__(self, _dict):
        self.__dict__.update(_dict)

    def __hash__(self):
        return self.path.__hash__()

    def __eq__(self, other):
        return self.path == other.path

    def save(self):
        with open(self.path, 'wb') as o:
            pickle.dump(self, o)

    def delete(self):
        os.remove(self.path)
        os.remove(self.database_path)
