#!/bin/bash

parcours()
{
    for i in `ls`; do
	if [ -d "$i" ]; then
	    cd "$i"
	    parcours
	    cd -
	elif test ${i##*.} = 'py'; then
	   ./"$i"
	fi
    done
}

parcours
