from pinscher.Keyfile import Keyfile
from pinscher.Database import Database


class Pinscher:

    def __init__(self, keyfile_path, **kwargs):
        self._keyfile = Keyfile(keyfile_path, **kwargs)

    def __enter__(self):
        self._database = Database(self._keyfile)
        return self

    def __exit__(self, type, value, traceback):
        self._database.save()
        self._keyfile.save()

    def add(self, secret):
        pass

    def search(self, tags):
        pass
