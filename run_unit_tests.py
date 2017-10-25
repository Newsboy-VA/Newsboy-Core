#!/usr/bin/env python3
import doctest
import os
import unittest


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(my_module_with_doctests))
    return tests

if __name__ == "__main__":
    for file in os.listdir("unit_tests"):
        if file.endswith(".txt"):
            print(file)
            doctest.testfile("unit_tests/"+file)
