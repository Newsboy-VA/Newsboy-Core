

class ActionBase(dict):
    ''' The base class for actions/intents '''
    def __init__(self, *args):
        super().__init__(*args)
        self.assert_items()

    def assert_items(self):
        ''' Ensure the class has the correct keys '''
        assert(isinstance(self['function'], str))
        if isinstance(self['arguments'], list):
            self['arguments'] = dict.fromkeys(self['arguments'])
        assert(isinstance(self['arguments'], dict))

    def __str__(self):
        string_representation = "{}(".format(self['function'])
        for arg in self['arguments'].keys():
            string_representation += "{}, ".format(arg)
        if len(self['arguments']) != 0:
            string_representation = string_representation[:-2]
        string_representation += ")"
        return string_representation
