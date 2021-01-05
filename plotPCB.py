#!/usr/bin/env sh
# -*- mode: Python -*-

""":"
if [[ "$OSTYPE" == "darwin"* ]]; then
    PYBIN="/Applications/Kicad/kicad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python"
else
    PYBIN="/usr/bin/env python3"
fi
exec ${PYBIN} "$0" "$@"
":"""

import sys
if sys.platform == 'darwin':
    sys.path.insert(
        0,
        "/Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/"
    )
import pcbnew
from pcbnew import *


def processBoard(boardName, plotDir):
    """Convert layers of KiCad PCB to SVGs"""
    print(boardName)
    print(plotDir)
    # Load board and initialize plot controller
    board = pcbnew.LoadBoard(boardName)
    boardBox = board.ComputeBoundingBox()
    boardXl = boardBox.GetX()
    boardYl = boardBox.GetY()
    boardWidth = boardBox.GetWidth()
    boardHeight = boardBox.GetHeight()
    print(boardXl, boardYl, boardWidth, boardHeight)

    pctl = pcbnew.PLOT_CONTROLLER(board)
    pctl.SetColorMode(True)

    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(plotDir)
    popt.SetPlotFrameRef(False)
    popt.SetLineWidth(pcbnew.FromMM(0.15))
    popt.SetAutoScale(False)
    popt.SetScale(2)
    popt.SetMirror(False)
    popt.SetUseGerberAttributes(True)
    popt.SetExcludeEdgeLayer(False)
    popt.SetUseAuxOrigin(True)

    layers = [
        ("F_Cu", pcbnew.F_Cu, "Top layer"),
        ("B_Cu", pcbnew.B_Cu, "Bottom layer"),
        ("B_Paste", pcbnew.B_Paste, "Paste bottom"),
        ("F_Paste", pcbnew.F_Paste, "Paste top"),
        ("F_SilkS", pcbnew.F_SilkS, "Silk top"),
        ("B_SilkS", pcbnew.B_SilkS, "Silk top"),
        ("B_Mask", pcbnew.B_Mask, "Mask bottom"),
        ("F_Mask", pcbnew.F_Mask, "Mask top"),
        ("Edge_Cuts", pcbnew.Edge_Cuts, "Edges"),
        ("Margin", pcbnew.Margin, "Margin"),
        ("In1_Cu", pcbnew.In1_Cu, "Inner1"),
        ("In2_Cu", pcbnew.In2_Cu, "Inner2"),
        ("Dwgs_User", pcbnew.Dwgs_User, "Dwgs_User"),
        ("Cmts_User", pcbnew.Cmts_User, "Comments_User"),
        ("Eco1_User", pcbnew.Eco1_User, "ECO1"),
        ("Eco2_User", pcbnew.Eco2_User, "ECO2"),
        ("B_Fab", pcbnew.B_Fab, "Fab bottom"),
        ("F_Fab", pcbnew.F_Fab, "Fab top"),
        ("B_Adhes", pcbnew.B_Adhes, "Adhesive bottom"),
        ("F_Adhes", pcbnew.F_Adhes, "Adhesive top"),
        ("B_CrtYd", pcbnew.B_CrtYd, "Courtyard bottom"),
        ("F_CrtYd", pcbnew.F_CrtYd, "Courtyard top"),
    ]

    for layer_info in layers:
        pctl.SetLayer(layer_info[1])
        pctl.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_SVG, layer_info[2])
        pctl.PlotLayer()

    return (boardXl, boardYl, boardWidth, boardHeight)


if __name__ == "__main__":

    boardName = sys.argv[1]
    plotDir = sys.argv[2]
    processBoard(boardName, plotDir)
