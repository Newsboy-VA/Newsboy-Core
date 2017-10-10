

# List of entities used within this module
entities = [
    {   "name": "",
        "parameters": []
    },
]

# List of intents this module can be used for
intents = [
    {
        "name": "",
        "synonyms": [],
        "templates": [],
        "responses": [
            {
                "action": "function_handle",
                "parameters": [],
            }
        ],
    },
]

class Module(object):
    """docstring for Module."""



    def __init__(self, arg):
        super(Service, self).__init__()
        self.arg = arg

        self.activeRequests = []

    def receiveRequest(request):
        client_id = request.id
        intent = request.intent


    def sendRequest(request):



    # def countdown_timer(user_id, time):

    # def start_timer_thread(uesr, time):
    #     # while timer:
    #
    #     send.alamrmessag(user, urgent)
    #     send.msg(user, non-urgent)
    # def set_appliance(appliance, state):
    #     pin.write(high, aplliance_pin)
    #
    #     send.response(msg, priority)




    # entities = [
    #         {   "name": "",
    #             "parameters": [
    #             ]
    #         },
    #         {   "name": "date",
    #             "parameters": [
    #                 "now",
    #                 "tomorrow",
    #                 "next week"
    #             ]
    #         },
    #         {   "name": "state",
    #             "parameters": [
    #                 "on",
    #                 "off"
    #             ]
    #         },
    #         {   "name": "appliance",
    #             "parameters": [
    #                 "heating",
    #                 "oven",
    #                 "toaster",
    #                 "kitchen lights"
    #             ]
    #
    #         }
    # ]
    #
    #
    # intents = [
    #     {
    #         "name": "set",
    #         "synonyms": [
    #             "turn",
    #             "switch"
    #         ],
    #         "action": "function_handle",
    #         "parameters": [ "appliance", "state" ],
    #      },
    # ]
