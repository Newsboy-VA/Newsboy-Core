

class ActionBase(dict):
    ''' The base class for actions/intents '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert(isinstance(self['name'], str))
        assert(isinstance(self['synonyms'], list))
        assert(isinstance(self['callback'], str))
        if isinstance(self['arguments'], list):
            self['arguments'] = dict.fromkeys(self['arguments'])
        assert(isinstance(self['arguments'], dict))

    def __str__(self):
        string_representation = "{}(".format(self.callback.__name__)
        for arg in self.argument_dict.keys():
            string_representation += "{}, ".format(arg)
        if len(self.argument_dict) != 0:
            string_representation = string_representation[:-2]
        string_representation += ")"
        return string_representation
