import string
import pickle

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

    def save(self):
        pickle.dump(self, open(self.path, 'wb'))
