import random
import string
from Vault import Vault


class Credentials(object):

    def __init__(self, domain, username, encrypted_password):
        self.domain = domain
        self.username = username
        self.encrypted_password = encrypted_password

    def get_password(self, pin):
        key, iv = Vault.make_key_iv(pin, self.domain, self.username)
        password = Vault.decrypt(key, iv, self.encrypted_password)
        try:
            return unicode(password)
        except UnicodeDecodeError:
            return self.generate()

    def generate(self, size=10):
        return u''.join(random.choice(string.digits + string.letters + string.punctuation) for x in range(size))
