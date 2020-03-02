# KiCad-Diff

This is a python program with a Tk inteface for comparing KiCad PCB revisions.

The diffing strategy has been changed for this version and SVGs are generated directly rather than doing renderings in ImageMagick as in previous versions. This has made the rendering possible for all layers in a few seconds (compared to 20-60s+ depending on resolution and number of layers selected in previous version).

The output is presented as a gallery of images of each layer. Each layer pair can be compared and the combined view highlights clearly where the layers differ from each other.

Was originaly a bash script, this newer GUI version has been rewritten in Python3 and supports Git, SVN and Fossil as SCM tools. I have also removed many of the dependencies.
 

**Instructions**
  *  Check that the paths to your SCM tools are correct (lines 39-45)
  *  Install plotPCB2.py in /usr/local/bin (or adjust path in lines 45 to suit). 
  *  Run the main script and select a pair of versions in a source controlled repository from the GUI.

  The script should build a series of svg files and display the diff in a webpage.
 

  Plans:
  Improvement in parsing and meaning of text diffs.
  Place all template text/css text in external files.
  Improve display of artifacts in diff choice window.
  Consider changing GUI elements to wxPython.
  Adjust <div> for three pane output to have white outer border & pan-zoom control, not filter colour.
  Improve three pane output layout, perhaps with diff tree on LHS and not underneath.

  ## Screenshots
GUI
![GUI](/Documents/gui.png)
![GUI](/Documents/gui2.png)

Overview
![Overview](/Documents/overview.png)

Main view
![Main](/Documents/main1.png)
![Main](/Documents/main2.png)

Diff
![Fab Layer Diff](/Documents/diff.png)

Fab Layer 
![Fab layer side by side](/Documents/pair.png)

Cu Layer
![Cu difference view](/Documents/cu.png)
![Cu layer - 3 pane view](/Documents/composite.png)

