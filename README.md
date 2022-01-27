# KiCad-Diff

This is a python program for comparing KiCad PCB revisions.


The layers of a Kicad board are exported to svg and output is presented as a gallery of images on a webpage. Each layer pair can be compared and the combined view highlights clearly where the layers differ from each other.

The diff output can be scrolled and zoomed in and out for closer inspection. The pair of 'before and after' views will also pan and zoom together. I have looked at linking all three windows together but this makes for a very confusing and unsatisfactory effect.

## Instructions

### Dependencies

- Ensure that you have Python3 installed. Why? https://www.pythonclock.org
- Python Libraries from Kicad 5.* or 6.*
- For python dependencies check the `requirements.txt`

To install KiCad-Diff dependencies:

```
cd KiCad-Diff
pip3 install -r requirements.txt
```

#### wxWidgets

This version uses wxWidgets for the GUI

To install it on macOS
```
brew install wxmac
brew install wxpython
```

To install it on Ubuntu
```
sudo apt install python3-wxgtk4.0
```

#### Kicad 6 Workaround

The new version of Kicad is generating svg files that do not work well on browsers (Google-Chrome, Firefox and Safari)
The `kicad6_svg_fix` script is a quick fix while we don't receive an improved version from Kicad team.
This requires the `rsvg-convert` tool.

To install it on macOS
```
brew install librsvg
```

To install it on Ubuntu
```
sudo apt install librsvg2-bin
```

## Usage

Make sure you have SCMs (Git, Fossil and/or SVN) available through the PATH variable.
Add the script path to your PATH too so the `kidiff` and `plot_kicad_pcb` will be available.
This can be done easily with:

```
cd KiCad-Diff
source env.sh
```

The terminal should give you some useful information on progress. Please include a copy of the terminal output if you have any issues.

### Command line help

```
usage: kidiff [-h] [-a COMMIT1_HASH] [-b COMMIT2_HASH] [-g] [-s SCM] [-d DISPLAY] [-p PORT] [-w] [-v] [-o OUTPUT_DIR] [-l] [-f] [PCB_PATH]

Kicad PCB visual diffs.

positional arguments:
  PCB_PATH              Kicad PCB path

optional arguments:
  -h, --help            show this help message and exit
  -a COMMIT1_HASH, --commit1-hash COMMIT1_HASH
                        Commit 1 hash
  -b COMMIT2_HASH, --commit2-hash COMMIT2_HASH
                        Commit 2 hash
  -g, --gui             Use gui
  -s SCM, --scm SCM     Select SCM (git, svn, fossil)
  -d DISPLAY, --display DISPLAY
                        Set DISPLAY value, default :1.0
  -p PORT, --port PORT  Set webserver port
  -w, --webserver-disable
                        Does not execute webserver (just generate images)
  -v, --verbose         Increase verbosity (-vvv)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Set output directory. Default is '.kidiff'.
  -l, --list-commits    List commits and exit
  -f, --frame           Plot whole page frame

```

### Usage example

```
# With a Git repo
kidiff led_test.kicad_pcb

# Forcing an specific SCM when more than one is available (Precedence: Git > Fossil > SVN)
kidiff led_test.kicad_pcb --scm fossil

# With a SVN repo, passing commit 1 and 2 on the command line
kidiff led_test.kicad_pcb -a r1 -b r3

```

## Debugging

There should be some output in the launch terminal. Please copy this and include it in any issues posted. If the program is not working, please check that you can run the `plot_kicad_pcb` routine directly by invoking it from the command line and passing the name of the `*.kicad_pcb` file.

```
plot_kicad_pcb board.kicad_pcb
```


# Screenshots

<p align="center">
  <img src="/docs/gui.png" width="550" alt="gui">
  <br>
  wxWidget GUI
</p>

<p align="center">
  <img src="/docs/main1.png" width="820" alt="main1">
  <br>
  Main View
</p>

<p align="center">
  <img src="/docs/main2.png" width="820" alt="main2">
  <br>
</p>

<p align="center">
  <img src="/docs/diff.png" width="300" alt="fab layer diff">
  <br>
  Overlapped Diff (F.Fab layer)
</p>

<p align="center">
  <img src="/docs/cu.png" width="350" alt="Cu difference view">
  <br>
  Top Layer (F.Cu)
</p>

<p align="center">
  <img src="/docs/pair.png" width="650" alt="fab layer side by side">
  <br>
  Comparison Side-by-Side View
</p>

<p align="center">
  <img src="/docs/composite.png" width="500" alt="Cu layer - 3 pane view">
  <br>
  3 Panel views together
</p>

<p align="center">
  <img src="/docs/text.png" width="850" alt="Text Diff">
  <br>
  Attributes Diff
</p>

