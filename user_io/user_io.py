

class UserIO(object):
    """docstring for UserIO."""

    def write(self,text):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def resume_reading(self):
        pass

    def stop_reading(self):
        pass
