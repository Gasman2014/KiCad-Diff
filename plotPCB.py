#!/usr/bin/env python3

'''
Kicad plot pcb file.
Plot variety of svg files in plot directory
'''

from pcbnew import *

# Load board and initialize plot controller
boardName = sys.argv[1]
plotDir = sys.argv[2]
reqLayers = []

file = open('/tmp/svg/layers', 'r')
reqLayers = [line.strip() for line in file]

print(reqLayers)


board = LoadBoard(boardName)
nets = pcbnew.NETINFO_LIST(board)
print(nets)
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
popt.SetUseAuxOrigin(False)


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
    if layer_info[2] in reqLayers:
        pctl.SetLayer(layer_info[1])
        pctl.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_SVG, layer_info[2])
        pctl.PlotLayer()
pctl.ClosePlot()
