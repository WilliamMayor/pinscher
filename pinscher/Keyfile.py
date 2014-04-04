import string
import pickle

import utilities


class Keyfile:

    LENGTH = 32
    CHARACTERS = string.digits + string.letters + string.punctuation + ' '
    FIELDS = {
        'database_path': lambda: None,
        'key': utilities.generate_key,
        'iv': utilities.generate_iv,
        'characters': lambda: Keyfile.CHARACTERS,
        'length': lambda: Keyfile.LENGTH
    }

    def __init__(self, path, **kwargs):
        self.path = path
        try:
            with open(self.path, 'rb') as fd:
                d = pickle.load(fd)
                self._pickled = d
        except:
            d = {}
            self._pickled = None
        for k, v in Keyfile.FIELDS.iteritems():
            if k in kwargs:
                self.__dict__[k] = kwargs[k]
            elif k in d:
                self.__dict__[k] = d[k]
            else:
                self.__dict__[k] = v()

    def save(self):
        d = {k: self.__dict__[k] for k in Keyfile.FIELDS}
        if self._pickled != d:
            with open(self.path, 'wb') as fd:
                pickle.dump(d, fd)
