class Server:
    @classmethod
    def from_str(cls, string):
        ip, port = string.split(':')
        return cls(ip, int(port))

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return self.__dict__.get(attr, None)

    def __repr__(self):
        return '<Server: {0}>'.format(self)

    def __str__(self):
        return '{0}:{1}'.format(self.ip, self.port)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __iter__(self):
        for attribute in self.__dict__:
            if not attribute.startswith('_'):
                yield attribute

    def _get_name(self):
        return self.__dict__.setdefault('name', self.ip)

    def _set_name(self, name):
        self.__dict__['name'] = name

    name = property(_get_name, _set_name)

    def as_tuple(self):
        return (self.ip, self.port)
