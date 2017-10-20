import copy
from .nlu import nlu

class Context(object):
    """docstring for Context."""
    def __init__(self):
        super(Context, self).__init__()
        self.intents_list = []

    def is_empty(self):
        return self.intents_list == []

    def have_full_intent(self):
        for intent in self.intents_list:
            if None in intent.argument_dict.values():
                return False
        return True

    def get_first_full_intent(self):
        # Maybe add some more intellegince for choosing a full intent (most parameters or something)
        for intent in self.intents_list:
            if None not in intent.argument_dict.values():
                return intent

    def is_in_context(self, new_intent):
        for intent in self.intents_list:
            if intent.name == new_intent.name:
                return True
        return False

    def update_arguments(self,phrase):
        for intent in self.intents_list:
            arguments_in_phrase = nlu.find_args_for_intent(intent.name, phrase)
            if arguments_in_phrase is not None:
                intent.argument_dict.update({k:v for k,v in arguments_in_phrase.items() if v is not None})

    def update(self, new_intent):
        # intent.argument_dict.update(args)
        if not self.is_in_context(new_intent):
            self.intents_list.append(copy.copy(new_intent))
            print("Added new intent {} to the context".format(new_intent.name))
        else:
            for intent in self.intents_list:
                if intent.name == new_intent.name:
                    intent.argument_dict.update({k:v for k,v in new_intent.argument_dict.items() if v is not None})
                    print("Updating existing intent, {}. Arguments now: {}".format(intent.name, intent.argument_dict))

    def clear(self):
        self.intents_list = []


class Conversation(object):
    """docstring for Conversation."""
    def __init__(self, client):
        super(Conversation, self).__init__()

        # Who the conversation is with
        self.client = client

        self.my_turn = None
        self.ongoing = False
        self.context = Context()


    """ If newsboy is starting a conversation with the client.
        Else the conversation has been started by the client so this method is not needed.
    """
    def start(self, phrase=None):
        self.ongoing = True
        if phrase is not None:
            self.ask_client(phrase)

    def ask_client(self, phrase):
        self.client.write(phrase)

    def listen_to_client(self):
        return self.client.read()

    def converse(self, phrase = None):
        # if self.my_turn:
        #     self.ask_client(adjacency)
        #
        #     self.listen_to_client(expected_pair = adjacency)
        #
        # else:
        #     self.listen_to_client()
        #     respond()

        ''' ASK (an adjacency pair) If phrase is None then it is assumed the client will lead with an adjacency pair '''
        if phrase is not None:
            self.ask_client(phrase)

        ''' LISTEN '''
        client_response = self.listen_to_client()

        ''' RESPOND '''
        self.reply(client_response)

        # UNDERSTAND (expect the respective adjacency pair back)


    def reply(self, phrase):

        # Acknowledge
        self.client.write("You said '" + phrase + "'")

        # Understand intent of user
        for intent in nlu.find_intents_in_phrase(phrase):
            print("Intent found to be {} with arguments {}".format(intent.name, intent.argument_dict))
            self.context.update(intent)

        ''' Call function for users intent.
            If insufficient arguments prompt user for remaining arguments
        '''
        if not self.context.is_empty():
            self.context.update_arguments(phrase)
            if self.context.have_full_intent():
                self.client.write(" All arguments found for the {} intent. Calling function... ".format(self.context.get_first_full_intent().name))
                self.ongoing = False
            else:
                self.converse("What " + [entity for entity,value in self.context.intents_list[0].argument_dict.items() if value is None ][0])




        # phraseType = nlu.whatTypeOfPhrase()
        #
        # if phraseType = 'QUESTION':
        #     reply(answer)
        #
        #     response = nlu.deconstruct(client_response)
        # else if phraseType = 'STATEMENT':
        #
        #
        # # Build context/understanding of what the client wants
        # self.context.add(response)
        #
        # while no full_intent:
        #     self.converse()
        #
        # # REACT
        # carry out intent

    def end(self):
        self.conversation_ongoing = False
        self.client.write("Goodbye")

#
#
# """
#     Converstions have a:
#     - begining
#     - end
#
#     -Grice’s maxims,  the speakers and listeners support and evaluate each other using known building blocks: adjacency pairs and turns
#     (https://www.slideshare.net/bahrozshah/grices-maxims-75547851)
#
#     - turn-taking, turn-ending, feedback, turns(adjacency pairs)
#
#     adjacency pairs:
#
#     question - answer
#     statement - recognition
#     complaint - reply
#     greeting - exchange of greeting
#     request - accept
#     thanking - response
# """
