class Keyfile(object):

    def __init__(self, name, location, timeout):
        self.name = name
        self.location = location
        self.timeout = timeout
        self.db_uri = 'file:%s?mode=memory&cache=shared' % name
        with open(location, 'r') as keyfile:
            self.data_location = keyfile.readline().strip()
            self.iv = keyfile.readline().strip().decode('hex')
            self.key = keyfile.readline().strip().decode('hex')

    def to_dict(self):
        return {
            'name': self.name,
            'location': self.location,
            'timeout': self.timeout,
            'db_uri': self.db_uri,
            'data_location': self.data_location
        }
