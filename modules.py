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
board = pcbnew.LoadBoard(boardName)
for module in board.GetModules():
    print("Module Ref %s %s" % ( module.GetReference(), board.GetLayerName(module.Reference().GetLayer())))
