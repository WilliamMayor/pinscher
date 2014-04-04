import utilities


class Secret:

    def __init__(self, cipher=None, plain=None, tags=(), iv=None, pin=None):
        self.iv = iv
        self.tags = tags
        self.cipher = cipher
        self.plain = plain
        if pin is not None:
            self.lock(pin)
            self.unlock(pin)

    def unlock(self, pin):
        if self.plain is None:
            key = utilities.generate_key(pin, *self.tags)
            self.plain = utilities.decrypt(key, self.iv, self.cipher)

    def lock(self, pin):
        if self.cipher is None:
            if self.iv is None:
                self.iv = utilities.generate_iv()
            key = utilities.generate_key(pin, *self.tags)
            self.cipher = utilities.encrypt(key, self.iv, self.plain)

    def __repr__(self):
        return '<Secret tags=%s>' % str(self.tags)
