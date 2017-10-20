
class Context(object):
    """docstring for Context."""
    def __init__(self):
        super(Context, self).__init__()
        self.intent = None
        self.parameters = []

    def add(self):
        ''' '''

    def clear(self):
        self.intent = None
        self.parameters = []

class Conversation(object):
    """docstring for Conversation."""
    def __init__(self, client_io):
        super(Conversation, self).__init__()

        self.who = None
        self.client = client

        self.ongoing = False
        self.context = Context()
    #
    #
    # """ If newsboy is starting a conversation with the client.
    #     Else the conversation has been started by the client so this method is not needed.
    # """
    # def start(self, summons=None):
    #     self.conversation_ongoing = True
    #     if summons not None:
    #         client_io.say(summons)
    #

    def take_turn(self, phrase):
        # ASK (an adjacency pair)
        self.client.ask(phrase)

        # LISTEN/UNDERSTAND (expect the respective adjacency pair back)
        client_response = self.client.listen()
        response = nlu.deconstruct(client_response)

        # Build context/understanding of what the client wants
        self.context.add(response)
        if full intent in context:
            carry out intent


    def fill_context(response):



    def end():
        self.conversation_ongoing = False
        self.client_io.say("Goodbye")



"""
    Converstions have a:
    - begining
    - end

    -Grice’s maxims,  the speakers and listeners support and evaluate each other using known building blocks: adjacency pairs and turns

    - turn-taking, turn-ending, feedback, turns(adjacency pairs)

    adjacency pairs:

    question - answer
    statement - recognition
    complaint - reply
    greeting - exchange of greeting
    request - accept
    thanking - response
"""



def main():

    conversation = Conversation(text_client)

    conversation.start()
    while conversation.ongoing():
        conversation.take_turn()

        if

    conversation.end()
