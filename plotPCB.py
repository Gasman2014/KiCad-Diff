#!/usr/bin/env python3

'''
Plot layers of Kicad PCB board into .svg files
'''

import argparse
import sys

import platform
if platform.system() == 'Darwin':
    sys.path.insert(0,"/Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/")

from pcbnew import LoadBoard, PLOT_CONTROLLER, PLOT_FORMAT_SVG, FromMM
from pcbnew import \
    F_Cu, \
    In1_Cu, \
    In2_Cu, \
    In3_Cu, \
    In4_Cu, \
    B_Cu, \
    F_Adhes, \
    B_Adhes, \
    F_Paste, \
    B_Paste, \
    F_SilkS, \
    B_SilkS, \
    F_Mask, \
    B_Mask, \
    Dwgs_User, \
    Cmts_User, \
    Eco1_User, \
    Eco2_User, \
    Edge_Cuts, \
    Margin, \
    F_CrtYd, \
    B_CrtYd, \
    F_Fab, \
    B_Fab


def processBoard(boardName, plotDir, quiet):
    '''Load board and initialize plot controller'''

    board = LoadBoard(boardName)
    boardbox = board.ComputeBoundingBox()
    boardxl = boardbox.GetX()
    boardyl = boardbox.GetY()
    boardwidth = boardbox.GetWidth()
    boardheight = boardbox.GetHeight()

    if not quiet:
        print(boardxl, boardyl, boardwidth, boardheight)

    pctl = PLOT_CONTROLLER(board)
    pctl.SetColorMode(True)

    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(plotDir)
    popt.SetPlotFrameRef(False)
    popt.SetLineWidth(FromMM(0.15))
    popt.SetAutoScale(False)
    popt.SetScale(2)
    popt.SetMirror(False)
    popt.SetUseGerberAttributes(True)
    popt.SetExcludeEdgeLayer(False)
    popt.SetUseAuxOrigin(True)

    layers = [
        ("F_Cu",      F_Cu,      "Top copper"),
        ("In1_Cu",    In1_Cu,    "Inner1 copper"),
        ("In2_Cu",    In2_Cu,    "Inner2 copper"),
        ("In3_Cu",    In3_Cu,    "Inner3 copper"),
        ("In4_Cu",    In4_Cu,    "Inner4 copper"),
        ("B_Cu",      B_Cu,      "Bottom copper"),
        ("F_Adhes",   F_Adhes,   "Adhesive top"),
        ("B_Adhes",   B_Adhes,   "Adhesive bottom"),
        ("F_Paste",   F_Paste,   "Paste top"),
        ("B_Paste",   B_Paste,   "Paste bottom"),
        ("F_SilkS",   F_SilkS,   "Silk top"),
        ("B_SilkS",   B_SilkS,   "Silk top"),
        ("F_Mask",    F_Mask,    "Mask top"),
        ("B_Mask",    B_Mask,    "Mask bottom"),
        ("Dwgs_User", Dwgs_User, "User drawings"),
        ("Cmts_User", Cmts_User, "User comments"),
        ("Eco1_User", Eco1_User, "Eng change order 1"),
        ("Eco2_User", Eco2_User, "Eng change order 1"),
        ("Edge_Cuts", Edge_Cuts, "Edges"),
        ("Margin",    Margin,    "Margin"),
        ("F_CrtYd",   F_CrtYd,   "Courtyard top"),
        ("B_CrtYd",   B_CrtYd,   "Courtyard bottom"),
        ("F_Fab",     F_Fab,     "Fab top"),
        ("B_Fab",     B_Fab,     "Fab bottom")
    ]

    for layer_info in layers:
        pctl.SetLayer(layer_info[1])
        pctl.OpenPlotfile(layer_info[0], PLOT_FORMAT_SVG, layer_info[2])
        layer_name = board.GetLayerName(layer_info[1]).replace(".", "_")
        if layer_info[0] != layer_name:
            pctl.OpenPlotfile(layer_name, PLOT_FORMAT_SVG, layer_info[2])
        pctl.PlotLayer()

    return (boardxl, boardyl, boardwidth, boardheight)


def parse_cli_args():
    parser = argparse.ArgumentParser(description='Plot PCB Layers')
    parser.add_argument('-o', "--output_folder", type=str, help="Output folder")
    parser.add_argument('-q', "--quiet", action='store_true', help="Disable output")
    parser.add_argument("kicad_pcb", nargs=1, help="Kicad PCB")
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = parse_cli_args()

    boardName = args.kicad_pcb[0]

    if args.output_folder:
        plotDir = args.output_folder

    processBoard(boardName, plotDir, args.quiet)
