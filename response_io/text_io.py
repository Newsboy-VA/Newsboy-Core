#!/usr/bin/env python3


from response_io.response_io import ResponseIO


class TextIO(ResponseIO):
    """docstring for TextIO."""


    def write(self, text):
        if text is not "":
            print(text)

    def read(self, blocking=True):
        user_response = input()

        return user_response



if __name__ == "__main__":

    text_io = TextIO()

    while True:
        text = text_io.read()
        text_io.write(text)
