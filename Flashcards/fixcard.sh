#!/bin/bash

for f in $*
do
	convert -resize 456x -crop 456x391 $f ${f/-raw/-card}
done
