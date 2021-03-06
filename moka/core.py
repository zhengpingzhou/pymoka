import os


class g(object):
    HOME = os.path.expanduser('~')
    USER = os.environ['USER']


class Dict(object):
    def __init__(self, *args, **kwargs):
        assert len(args) <= 1

        if len(args) == 1:
            self.update(args[0])

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

    def __iter__(self):
        for k in vars(self): yield k

    def to_dict(self, d):
        if isinstance(d, dict): return d
        return vars(d)

    def items(self):
        return vars(self).items()

    def update(self, d):
        d = self.to_dict(d)
        for k, v in d.items():
            setattr(self, k, v)

    def get(self, key, default_value):
        return vars(self).get(key, default_value)