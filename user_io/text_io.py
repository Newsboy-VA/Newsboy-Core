#!/usr/bin/env python3


from user_io import UserIO


class TextIO(UserIO):
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
