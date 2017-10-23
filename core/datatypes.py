
class NamedObjectList(list):
    ''' A list of objects that can be referenced by their 'name' method. '''
    def __getitem__(self, key):
        if isinstance(key, str):
            for item in self:
                if item.name == key:
                    return item
            raise IndexError('no object named {!r}'.format(key))
        return list.__getitem__(self, key)

    def get(self, k, d=None):
        ''' D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None. '''
        for item in self:
            if item.name == k:
                return item
        return d
