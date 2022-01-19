#!/bin/bash

# Install Kicad plugin on Kicad v6
# kiti, kidiff and plotgitsh must be in PATH

case $OSTYPE in
	darwin*)
		KICAD_PLUGINS_PATH="$HOME/Library/Preferences/KiCad/scripting/plugins"
		;;
	*)
		KICAD_PLUGINS_PATH="$HOME/.local/share/kicad/6.0/scripting/plugins"
		;;
esac

mkdir -p "${KICAD_PLUGINS_PATH}"
rm -rf "${KICAD_PLUGINS_PATH}/kidiff"

cp -r "plugin" "${KICAD_PLUGINS_PATH}/kidiff"
