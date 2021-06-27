#!/bin/bash

# Python modules for the new PCBNew

case ${OSTYPE} in

	# MaxOS (update to your Kicad nightly path)
	darwin*)
		export PYTHONPATH="/Applications/KiCad/kicad.app/Contents/Frameworks/python/site-packages/"
		export LD_LIBRARY_PATH="${PYTHONPATH}"
		;;

	# Linux
	*)
		export PYTHONPATH="/usr/lib/kicad-nightly/lib/python3/dist-packages/"
		export LD_LIBRARY_PATH="${PYTHONPATH}"
		;;

esac


# Binaries
export PATH=$(pwd):${PATH}
