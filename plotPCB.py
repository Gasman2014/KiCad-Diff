#!/usr/bin/env python3

'''
Plot layers of Kicad PCB board into .svg files
'''

import argparse
import sys

import platform
if platform.system() == 'Darwin':
    sys.path.insert(0,"/Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/")

import pcbnew
from pcbnew import *


def processBoard(boardName, plotDir, quiet):
    '''Load board and initialize plot controller'''

    board = pcbnew.LoadBoard(boardName)
    boardbox = board.ComputeBoundingBox()
    boardxl = boardbox.GetX()
    boardyl = boardbox.GetY()
    boardwidth = boardbox.GetWidth()
    boardheight = boardbox.GetHeight()

    if not quiet:
        print(boardxl, boardyl, boardwidth, boardheight)

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

    # layers = [
    #     ("F_Cu", pcbnew.F_Cu, "Top layer"),
    #     ("B_Cu", pcbnew.B_Cu, "Bottom layer"),
    #     ("B_Paste", pcbnew.B_Paste, "Paste bottom"),
    #     ("F_Paste", pcbnew.F_Paste, "Paste top"),
    #     ("F_SilkS", pcbnew.F_SilkS, "Silk top"),
    #     ("B_SilkS", pcbnew.B_SilkS, "Silk top"),
    #     ("B_Mask", pcbnew.B_Mask, "Mask bottom"),
    #     ("F_Mask", pcbnew.F_Mask, "Mask top"),
    #     ("Edge_Cuts", pcbnew.Edge_Cuts, "Edges"),
    #     ("Margin", pcbnew.Margin, "Margin"),
    #     ("In1_Cu", pcbnew.In1_Cu, "Inner1"),
    #     ("In2_Cu", pcbnew.In2_Cu, "Inner2"),
    #     ("Dwgs_User", pcbnew.Dwgs_User, "Dwgs_User"),
    #     ("Cmts_User", pcbnew.Cmts_User, "Comments_User"),
    #     ("Eco1_User", pcbnew.Eco1_User, "ECO1"),
    #     ("Eco2_User", pcbnew.Eco2_User, "ECO2"),
    #     ("B_Fab", pcbnew.B_Fab, "Fab bottom"),
    #     ("F_Fab", pcbnew.F_Fab, "Fab top"),
    #     ("B_Adhes", pcbnew.B_Adhes, "Adhesive bottom"),
    #     ("F_Adhes", pcbnew.F_Adhes, "Adhesive top"),
    #     ("B_CrtYd", pcbnew.B_CrtYd, "Courtyard bottom"),
    #     ("F_CrtYd", pcbnew.F_CrtYd, "Courtyard top"),
    # ]

    layers = [
        ("F_Cu",      pcbnew.F_Cu,      "Top copper"),
        ("In1_Cu",    pcbnew.In1_Cu,    "Inner1 copper"),
        ("In2_Cu",    pcbnew.In2_Cu,    "Inner2 copper"),
        ("In3_Cu",    pcbnew.In3_Cu,    "Inner3 copper"),
        ("In4_Cu",    pcbnew.In4_Cu,    "Inner4 copper"),
        ("B_Cu",      pcbnew.B_Cu,      "Bottom copper"),
        ("F_Adhes",   pcbnew.F_Adhes,   "Adhesive top"),
        ("B_Adhes",   pcbnew.B_Adhes,   "Adhesive bottom"),
        ("F_Paste",   pcbnew.F_Paste,   "Paste top"),
        ("B_Paste",   pcbnew.B_Paste,   "Paste bottom"),
        ("F_SilkS",   pcbnew.F_SilkS,   "Silk top"),
        ("B_SilkS",   pcbnew.B_SilkS,   "Silk top"),
        ("F_Mask",    pcbnew.F_Mask,    "Mask top"),
        ("B_Mask",    pcbnew.B_Mask,    "Mask bottom"),
        ("Dwgs_User", pcbnew.Dwgs_User, "User drawings"),
        ("Cmts_User", pcbnew.Cmts_User, "User comments"),
        ("Eco1_User", pcbnew.Eco1_User, "Eng change order 1"),
        ("Eco2_User", pcbnew.Eco2_User, "Eng change order 1"),
        ("Edge_Cuts", pcbnew.Edge_Cuts, "Edges"),
        ("Margin",    pcbnew.Margin,    "Margin"),
        ("F_CrtYd",   pcbnew.F_CrtYd,   "Courtyard top"),
        ("B_CrtYd",   pcbnew.B_CrtYd,   "Courtyard bottom"),
        ("F_Fab",     pcbnew.F_Fab,     "Fab top"),
        ("B_Fab",     pcbnew.B_Fab,     "Fab bottom")
    ]

    for layer_info in layers:
        pctl.SetLayer(layer_info[1])
        pctl.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_SVG, layer_info[2])
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
