#!/bin/bash

# Please run setup.bash as sudo.
# Note that this is not yet complete.


# General
# sudo apt-get update

sudo apt-get install python3-dev python3-pip
sudo -H pip3 install --upgrade pip

# Speech-to-text (speech recognition)
sudo -H pip3 install pocketsphinx
sudo -H pip3 install pyaudio
sudo -H pip3 install SpeechRecognition

mkdir ./models ./models/en-us
cd ./models/en-us

wget "https://sourceforge.net/projects/cmusphinx/files/Acoustic and Language Models/US English/cmusphinx-en-us-5.2.tar.gz/download" -O cmusphinx-en-us-5.2.tar.gz
#gunzip cmusphinx-en-us-5.2.tar.gz
#tar -xf cmusphinx-en-us-5.2.tar
tar -xvzf cmusphinx-en-us-5.2.tar.gz
rm cmusphinx-en-us-5.2.tar.gz

wget "https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/US%20English/en-70k-0.2-pruned.lm.gz/download" -O en-70k-0.2-pruned.lm.gz
gunzip en-70k-0.2-pruned.lm.gz

wget "https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict"  -O cmudict-en-us.dict

cd ../../

# Text-to-speech
sudo apt-get install espeak
sudo apt-get install mbrola-en1  # or your choice. Not required

# Info module
sudo -H pip3 install feedparser

# Music module
sudo -H pip3 install python_vlc
sudo -H pip3 install youtube_dl
sudo -H pip3 install pafy
sudo -H pip3 install "psutil>=5.4.2"
sudo -H pip3 install num2words
