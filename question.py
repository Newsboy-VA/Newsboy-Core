

class Question(object):
    """docstring for Question."""




    def __init__(self, phrase_dict=None, io=None):
        super(self.__class__, self).__init__()

        if io is None:
            raise NotImplementedError
        self.io=io             # terminal/text, speech/stt, HTTP
        self.phrase_dict=phrase_dict
        self.affirmation="OK"

        # self.subject=None        # general conversation, music, weather, search, ...
        #     self.phrase_dict = None
        #     self.question_str=None


    def ask(self, question_str):

        # ASK
        # ----------------------------------------------------------------------
        if question_str is not None:
            self.io.write(question_str)

        # LISTEN
        # ----------------------------------------------------------------------
        user_response = self.io.read()
        # if acceptable_response(user_response):
        if self.affirmation is not None:
            self.io.write(self.affirmation)

        # else:
        #     io.say("NOT ACCEPTABLE!!!")

        self.io.resume_reading()





        # DO
        # ----------------------------------------------------------------------
        if self.phrase_dict is None:
            return user_response


        phrase_matches = []

        for phrase in self.phrase_dict.keys():
            is_match = True

            if isinstance(phrase, tuple):
                for word in phrase:
                    if word not in user_response:
                        is_match = False
            else:
                if phrase not in user_response:
                    is_match = False

            if is_match:
                phrase_matches.append(phrase)

        if phrase_matches != []:
            print(self.phrase_dict[phrase_matches[-1]])
            self.phrase_dict[phrase_matches[-1]](self.io)
