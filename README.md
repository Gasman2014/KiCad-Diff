# KiCad-Diff

This is a python program with a Tk interface for comparing KiCad PCB revisions.
  
The diffing strategy has been changed for this version and SVGs are generated directly rather than doing renderings in ImageMagick as in previous versions. This has made the rendering possible for all layers in a few seconds (compared to 20-60s+ depending on resolution and number of layers selected in previous version). The SVG images are layered together with a different feColorMatrix filter applied to each diff. This highlights areas where features have been added or removed.

The output is presented as a gallery of images of each layer. Each layer pair can be compared and the combined view highlights clearly where the layers differ from each other.

The diff output can be scrolled and zoomed in and out for closer inspection. The pair of 'before and after' views will also pan and zoom together. I have looked at linking all three windows together but this makes for a very confusing and unsatisfactory effect.

There is an additional 'Text Diff' which is helpful for identifying specific areas which have changed. Ongoing work to compare netlist directly.

This was originally written as a bash script, this newer GUI version has been rewritten in Python3 and supports Git, SVN and Fossil as SCM tools. I have also removed many of the dependencies.

## Instructions

- Check that the paths to your SCM tools are correct (lines 39-45). You do not need to install all of these but if you do not have one make sure that you set it to null  e.g. if you don't have SVN installed, make sure you set svnProg=''.
- Ensure that you have Python3 installed. Why? https://www.pythonclock.org 
- Install 'plotPCB.py' in /usr/local/bin (or adjust path in lines 45 to suit) This needs to be executable. This program actually generates the necessary SVG files.
- MacOS requires a bit of tweaking - KiCad on macOS uses a locally installed version of python and NOT the system python. For other *nix operating systems, the site-packages are installed under the system python so don't need any further adjustment. For macOS, use the 'plotPCB_macOS.py' file. This also assumes that KiCad is installed normally in the 'Applications' folder
- Run the main script and select a pair of versions in a source controlled repository from the GUI. The GUI should show which SCM is in use.
- The terminal should give you some useful information on progress. Please include a copy of this if you have any issues.
- Hit `Ctrl+C` to terminate the webserver.

The script should build a series of svg files and display the diff in a webpage. If a web page doesn't open automatically, navigate to "http://127.0.0.1:9090/web/index.html" to view the output. You can adjust the port used (9090 by default) if this conflicts with your existing set-up.


## Command Line Usage

```
➜ ./kidiff_linux.py -h
usage: kidiff_linux.py [-h] [-d DISPLAY] [-a COMMIT1] [-b COMMIT2] [-s SCM] [-g] [-p PORT] [-w] kicad_pcb

Kicad PCB visual diffs.

positional arguments:
  kicad_pcb             Kicad PCB

optional arguments:
  -h, --help            show this help message and exit
  -d DISPLAY, --display DISPLAY
                        Set DISPLAY value, default :1.0
  -a COMMIT1, --commit1 COMMIT1
                        Commit1
  -b COMMIT2, --commit2 COMMIT2
                        Commit2
  -s SCM, --scm SCM     Select SCM (Git, SVN, Fossil)
  -g, --gui             Use gui
  -p PORT, --port PORT  Set webserver port
  -w, --webserver-disable
                        Does not execute webserver (just generate images)
```

## Debugging

There should be some output in the launch terminal. Please copy this and include it in any issues posted. If the program is not working, please check that you can run the `plotPCB.py` routine directly by invoking it from the command line and passing it two arguments (1) The name of a `*.kicad_pcb` file and (2) a test directory for the plots to end up in;

```
plotPCB.py boar.kicad_pcb output_folder
```

## Next Steps

  1. Improvement in parsing and meaning of text diffs.
  2. Place all template text/css text in external files.
  3. Improve display of artifacts in diff choice window.
  4. Consider changing GUI elements to wxPython.
  5. Adjust for three pane output to have white outer border & pan-zoom control, not filter color.
  6. Improve three pane output layout, perhaps with diff tree on LHS and not underneath.
  7. Consider adding 'Preferences' for this program.


# Screenshots

### GUI
![GUI](/Documents/gui.png)

![GUI](/Documents/gui2.png)


### Overview
![Overview](/Documents/Overview.png)

### Main view
![Main](/Documents/main1.png)

![Main](/Documents/main2.png)


### Diff
![Fab Layer Diff](/Documents/diff.png)


### Fab Layer
![Fab layer side by side](/Documents/pair.png)


### F_Cu Layer
![Cu difference view](/Documents/cu.png)
![Cu layer - 3 pane view](/Documents/composite.png)

### Text Diff
![Text Diff](/Documents/text.png)
