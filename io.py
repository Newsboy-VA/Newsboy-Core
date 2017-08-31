

class IO(object):
    """docstring for IO."""
    def __init__(self, arg):
        super(IO, self).__init__()
        self.arg = arg

    def write(self,text):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def resume_reading(self):
        pass

    def stop_reading(self):
        pass
