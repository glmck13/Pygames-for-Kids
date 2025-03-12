#!/bin/bash

source $HOME/venv/bin/activate

while true
do
	cd $HOME/opt/Pygames-for-Kids
	export SDL_VIDEO_WINDOW_POS=40,0
	cmd=$(python3 app.py | tail -1)
	eval $cmd
done
