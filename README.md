# KiCad-Diff

This is a python program with a Tk interface for comparing KiCad PCB revisions.
  
The diffing strategy has been changed for this version and SVGs are generated directly rather than doing renderings in ImageMagick as in previous versions. This has made the rendering possible for all layers in a few seconds (compared to 20-60s+ depending on resolution and number of layers selected in previous version). The SVG images are layered together with a different feColorMatrix filter applied to each diff. This highlights areas where features have been added or removed.

The output is presented as a gallery of images of each layer. Each layer pair can be compared and the combined view highlights clearly where the layers differ from each other.

The diff output can be scrolled and zoomed in and out for closer inspection. The pair of 'before and after' views will also pan and zoom together. I have looked at linking all three windows together but this makes for a very confusing and unsatisfactory effect.

## Instructions

### General
- Ensure that you have Python3 installed. Why? https://www.pythonclock.org 
- The terminal should give you some useful information on progress. Please include a copy of this if you have any issues.
- Hit `Ctrl+C` to terminate the webserver.


## Usage

Make sure you have SCMs (Git, Fossil and/or SVN) available throught the PATH variable.
Add the script path to your PATH too so the `kidiff` and `kiplotpcb` will be available.
This can be done easely with:

```
cd KiCad-Diff
source env.sh
```

### Comandline help

```
➜ ./kidiff -h
usage: kidiff [-h] [-a COMMIT1] [-b COMMIT2] [-g] [-s SCM] [-d DISPLAY] [-p PORT] [-w] [-v] [PCB_PATH]

Kicad PCB visual diffs.

positional arguments:
  PCB_PATH              Kicad PCB path

optional arguments:
  -h, --help            show this help message and exit
  -a COMMIT1, --commit1 COMMIT1
                        Commit 1
  -b COMMIT2, --commit2 COMMIT2
                        Commit 2
  -g, --gui             Use gui
  -s SCM, --scm SCM     Select SCM (git, svn, fossil)
  -d DISPLAY, --display DISPLAY
                        Set DISPLAY value, default :1.0
  -p PORT, --port PORT  Set webserver port
  -w, --webserver-disable
                        Does not execute webserver (just generate images)
  -v, --verbose         Increase verbosity (-vvv)

```

### Usage example

```
# Forcing an specific SCM when both are available (Precedence: Git > Fossil > SVN)
kidiff ../scms-samples/led-board-git-fossil/led_test.kicad_pcb --scm fossil

# With a Git repo
kidiff ../scms-samples/led-board-git/led_test.kicad_pcb             

# With a Git repo, passing Commit 1 and 2 on the command line
kidiff ../scms-samples/led-board-svn/led_test.kicad_pcb -a r1 -b r3

```

## Debugging

There should be some output in the launch terminal. Please copy this and include it in any issues posted. If the program is not working, please check that you can run the `plotPCB.py` routine directly by invoking it from the command line and passing it two arguments (1) The name of a `*.kicad_pcb` file and (2) a test directory for the plots to end up in;

```
plotPCB.py board.kicad_pcb output_folder
```

<!-- NEXT Steps was removed. It is better to put this on Wiki -->
<!-- ## Next Steps

  1. Improvement in parsing and meaning of text diffs.
  2. Place all template text/css text in external files.
  3. Improve display of artifacts in diff choice window.
  4. Consider changing GUI elements to wxPython.
  5. Adjust for three pane output to have white outer border & pan-zoom control, not filter color.
  6. Improve three pane output layout, perhaps with diff tree on LHS and not underneath.
  7. Consider adding 'Preferences' for this program.
 -->

# Screenshots

### GUI
<img src="/docs/gui.png" width="550" alt="gui">

### Main View
<img src="/docs/main1.png" width="820" alt="main1">
<img src="/docs/main2.png" width="820" alt="main2">

### Overlaped Diff
<img src="/docs/diff.png" width="300" alt="fab layer diff">

### Side-by-Side View
<img src="/docs/pair.png" width="600" alt="fab layer side by side">

### F_Cu Layer
<img src="/docs/cu.png" width="500" alt="Cu difference view">

### F_Cu Layer 3 Pane View
<img src="/docs/composite.png" width="500" alt="Cu layer - 3 pane view">

### Attributes Diff
<img src="/docs/text.png" width="850" alt="Text Diff">