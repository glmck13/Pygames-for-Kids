#!/bin/bash

source $HOME/venv/bin/activate

cd $HOME/opt/Pygames-for-Kids/Spell-and-Tell
export SDL_VIDEO_WINDOW_POS=40,0
python3 spell.py
