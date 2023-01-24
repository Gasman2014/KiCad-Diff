#!/bin/bash

# Install Kicad plugin on Kicad v6
# kiti, kidiff and plotgitsh must be in PATH

install_plugin_on_kicad()
{
	kicad_version="$1"

	case ${OSTYPE} in
		darwin*) KICAD_PLUGINS_PATH="${HOME}/Library/Preferences/kicad/${kicad_version}/scripting/plugins" ;;
		*) KICAD_PLUGINS_PATH="${HOME}/.local/share/kicad/${kicad_version}/scripting/plugins" ;;
	esac

	mkdir -p "${KICAD_PLUGINS_PATH}"
	rm -rf "${KICAD_PLUGINS_PATH}/kidiff"
	cp -r "plugin" "${KICAD_PLUGINS_PATH}/kidiff"
}

install_plugin_on_kicad "6.0"
install_plugin_on_kicad "6.99"
install_plugin_on_kicad "7.0"
