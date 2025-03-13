#!/bin/bash

source $HOME/venv/bin/activate

cd $HOME/opt/Pygames-for-Kids/Flashcards
export SDL_VIDEO_WINDOW_POS=40,0
shuf cards.csv | python3 cards.py
