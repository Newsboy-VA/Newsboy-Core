import copy
from nlu import NLU
import asyncio


nlu = NLU()

class Context(object):
    """docstring for Context."""
    def __init__(self):
        super(Context, self).__init__()
        self.intents_list = []

    def is_empty(self):
        return self.intents_list == []

    def have_full_intent(self):
        for intent in self.intents_list:
            if None in intent['arguments'].values():
                return False
        return True

    def get_first_full_intent(self):
        # Maybe add some more intelligence for choosing a full intent (most parameters or something)
        for intent in self.intents_list:
            if None not in intent['arguments'].values():
                return intent

    def is_in_context(self, new_intent):
        for intent in self.intents_list:
            if intent.name == new_intent.name:
                return True
        return False

    def update_arguments(self,phrase):
        for intent in self.intents_list:
            arguments_in_phrase = nlu.find_args_for_intent(intent['function'], phrase)
            if arguments_in_phrase is not None:
                intent['arguments'].update({k:v for k,v in arguments_in_phrase.items() if v is not None})

    def update(self, new_intent):
        # intent.argument_dict.update(args)
        if not self.is_in_context(new_intent):
            self.intents_list.append(copy.copy(new_intent))
            # self.speak_to_client("Added new intent {} to the context".format(new_intent.name))
        else:
            for intent in self.intents_list:
                if intent.name == new_intent.name:
                    intent['arguments'].update({k:v for k,v in new_intent['arguments'].items() if v is not None})
                    # self.speak_to_client("Updating existing intent, {}. Arguments now: {}".format(intent.name, intent.argument_dict))

    def clear(self):
        self.intents_list = []


class Conversation(object):
    """docstring for Conversation."""
    def __init__(self, client):
        # Who the conversation is with
        self.client = client
        self.my_turn = None
        self.ongoing = False
        self.context = Context()

        self.start()

    def start(self, phrase=None):
        self.ongoing = True
        if phrase is not None:
            self.speak_to_client(phrase)

    def speak_to_client(self, phrase):
        self.client.write(phrase)

    @asyncio.coroutine
    async def listen_to_client(self):
        return await self.client.read()

    @asyncio.coroutine
    async def converse(self, phrase = None):
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
            self.speak_to_client(phrase)

        ''' LISTEN '''
        client_response = await self.listen_to_client()

        ''' RESPOND '''
        return await self.reply(client_response)


        # UNDERSTAND (expect the respective adjacency pair back)

    @asyncio.coroutine
    async def reply(self, phrase):
        # Acknowledge
        # self.speak_to_client("You said '" + phrase + "'\n")
        # Understand intent of user
        for intent in nlu.find_intents_in_phrase(phrase):
            # self.speak_to_client("Intent found to be {} with arguments {}\n".format(intent.name, intent.argument_dict))
            self.context.update(intent)

        ''' Call function for users intent.
            If insufficient arguments prompt user for remaining arguments
        '''
        if not self.context.is_empty():
            self.context.update_arguments(phrase)
            if self.context.have_full_intent():
                self.speak_to_client(" All arguments found for the {} intent. Calling function...".format(self.context.get_first_full_intent()['function']))
                self.ongoing = False
                return self.context.get_first_full_intent()
            else:
                await self.converse("What " + [entity for entity,value in self.context.intents_list[0]['arguments'].items() if value is None ][0] + " ? ")




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

    def end(self, phrase=None):
        self.ongoing = False
        if phrase is not None:
            self.speak_to_client(phrase + "\n")

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
