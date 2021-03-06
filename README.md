# Newsboy-Core

With a quick browse through Github, one can find many virtual assisstants - [Melissa](https://github.com/Melissa-AI/Melissa-Core), [Jarvis](https://github.com/sukeesh/Jarvis), [Athena](https://github.com/rcbyron/hey-athena-client), and some [nameless ones](https://github.com/brmson/Personal-Assistant). With such a wealth of other great projects to choose from, why make this one? For one, because making it is fun. But more importantly, there are some things that (I believe) set this one apart:

## No internet connection required
Many other virtual assistants require an internet connection for NLU or speech recognition. While you have the option to use online services, nothing requires an internet connection, so it can work in your car. Note that at this stage, using the online google speech-to-text service is way better than pocketsphinx.

## Dynamic NLU
Other projects that don't use online services seems to have a fairly simple way of responding. Newsboys Natural Language Understanding (NLU) works offline, and can have an increase in vocabulary while running.

## Support for multiple interfaces
You can have multiple 'clients' connected to Newsboy, which means you can connect to him from other computers (and more importantly, he can have multiple control panels around the house). Not only that, but each client can have a different way of intereacting with the user - command-line, speech, or through an internet browser.

## Modular design for developers
We have taken a very modular approach, so it is fairly easy to add new ways to connect to him, new users, and to add new modules. In fact, he (will) even has his own package manager!

## Easily configurable
The name of this assistant (Newsboy) has not made it into the code anywhere, except as a default configuration. You can change the name, how you want to interact, what the voice is etc. There is support for multiple users, each with their own preferences. In the long-term, hopefully Newsboy will be able to use computer vision to detect the user.

**Note:** He is currently very early in development so is not yet functional,
these points are just what the block diagrams and program design will allow.
You may be able to type to Newsboy through the terminal, but it may be months
before the first release.


# Installation Instructions

At this point, Newsboy only works on Linux (tested on Mint 18) with Python 3.5+
due to the async keywords. May change in the future or be ported to other
platforms, but that's low priority.

    git clone git@github.com:Newsboy-VA/Newsboy-Core.git
    cd Newsboy-Core
    ./setup.bash

This should install the dependencies, if not then raise an issue or submit a
pull request.

# Running Instructions

In order to get anything visible to work, three things need to be running:

1. The Newsboy Core (`core/core.py`)
2. One or more modules (`modules/*/main.py`)
3. One or more clients (your interface) (`client/client.py`)

Rather than running these individually, it's best to use the launcher in the
main directory, `virtual_assistant.py`. From this, you can launch individual
parts, or all at once, `virtual_assistant.py -h` for help.
