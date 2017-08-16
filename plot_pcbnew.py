#!/Applications/Kicad/kicad.app/Contents/Applications/pcbnew.app/Contents/MacOS/Python

"""
Kicad plot pcb file.
Plot variety of svg files in plot directory as well as pdf of double size
assembly guide
"""

import sys
sys.path.insert(0, "/Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/")
import pcbnew
from pcbnew import *

# Load board and initialize plot controller
boardName = sys.argv[1]
filePath = sys.argv[2]
board = LoadBoard(boardName)
pctl = pcbnew.PLOT_CONTROLLER(board)
popt = pctl.GetPlotOptions()
plotDir = filePath

popt.SetOutputDirectory(plotDir)
popt.SetPlotFrameRef(False)
popt.SetLineWidth(pcbnew.FromMM(0.15))
popt.SetAutoScale(False)
popt.SetScale(1)
popt.SetMirror(False)
popt.SetUseGerberAttributes(True)
popt.SetExcludeEdgeLayer(False)
popt.SetUseAuxOrigin(True)
pctl.SetColorMode(True)


# Assembly guide PDF
#popt.SetScale(2)
#pctl.SetLayer(pcbnew.F_SilkS)
#pctl.OpenPlotfile("Silk", pcbnew.PLOT_FORMAT_PDF, "Assembly guide")
#pctl.PlotLayer()
#popt.SetScale(1)

layers = [
    ("F_Cu", pcbnew.F_Cu, "Top layer"),
    ("B_Cu", pcbnew.B_Cu, "Bottom layer"),
    ("B_Paste", pcbnew.B_Paste, "Paste Bottom"),
    ("F_Paste", pcbnew.F_Paste, "Paste top"),
    ("F_SilkS", pcbnew.F_SilkS, "Silk top"),
    ("B_SilkS", pcbnew.B_SilkS, "Silk top"),
    ("B_Mask", pcbnew.B_Mask, "Mask bottom"),
    ("F_Mask", pcbnew.F_Mask, "Mask top"),
    ("Edge_Cuts", pcbnew.Edge_Cuts, "Edges"),
]

# popt.SetColor(COLOR4D(0.050, 0.050, 0.050, 0.1))
# Ideally would set colour of layer with the 'SetColor' method which was previosly descibed with colour names
# e.g.popt.SetColor(YELLOW) - this does not work and, although the COLOR4D doesn't cause an error it doesn't work.
# Nor does setting an integer work.

for layer_info in layers:
  pctl.SetLayer(layer_info[1])
  pctl.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_SVG, layer_info[2])
  pctl.PlotLayer()

# One approach is to write to html and use a 'greyed' filter
# github - aktos-io kicad-tols
#
# Alternative approach is produce a pile of svg fileas nad post process them to add colour
# see http://scottbezek.blogspot.co.uk/2016/04/scripting-kicad-pcbnew-exports.html
# At the end you have to close the last plot, otherwise you don't know when
# the object will be recycled!
pctl.ClosePlot()
