import utilities


class Credentials:

    def __init__(self, domain, username, cipherpassword=None, iv=None, plainpassword=None):
        self.domain = domain
        self.username = username
        self.cipherpassword = cipherpassword
        self.iv = iv
        self.plainpassword = plainpassword

    def unlock(self, pin):
        if self.plainpassword is None:
            key = utilities.generate_key(self.domain, self.username, pin)
            self.plainpassword = utilities.decrypt(key, self.iv, self.cipherpassword)
        return self.plainpassword

    def lock(self, pin):
        if self.cipherpassword is None:
            if self.iv is None:
                self.iv = utilities.generate_iv()
            key = utilities.generate_key(self.domain, self.username, pin)
            self.cipherpassword = utilities.encrypt(key, self.iv, self.plainpassword)
        return self.cipherpassword, self.iv

    def __eq__(self, other):
        equal = True
        if self.iv is not None and other.iv is not None:
            equal = equal and (self.iv == other.iv)
        return equal and (self.domain == other.domain) and (self.username == other.username)

    def __repr__(self):
        return '<Credentials %s %s %s %s %s>' % (self.domain, self.username, self.plainpassword, self.cipherpassword.encode('hex'), self.iv.encode('hex'))
