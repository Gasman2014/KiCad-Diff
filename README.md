# KiCad-Diff

This is a Python program that compares revisions of KiCad PCBs.

The layers of a KiCad board are exported to SVG, and the output is presented as a gallery of images on a web page. Each layer pair can be compared, and the combined view clearly highlights where the layers differ from one another.

The diff output can be scrolled and zoomed in and out for closer inspection. The pair of "before and after" views will also pan and zoom together.

## Instructions

### Dependencies

- Ensure that you have Python3 installed. Why? https://www.pythonclock.org
- Python Libraries from Kicad 5.* or 6.*
- For extra python dependencies check the `requirements.txt`

#### wxWidgets

_On macOS_ using Apple sillicon, you should export these flags first
```bash
export CFLAGS=-I/$(brew --prefix)/include
export CXXFLAGS=-I/$(brew --prefix)/include
```

_On Ubuntu_, wxWidgets can be installed with:
```bash
sudo apt install python3-wxgtk4.0
```

#### Installing dependencies

```bash
cd KiCad-Diff
pip3 install -r requirements.txt
```

## Usage

Make sure you have SCMs (Git, Fossil and/or SVN) available through the PATH variable.
Add the script path to your PATH too so the `kidiff` and `plot_kicad_pcb` will be available.
This can be done easily with:

```bash
cd KiCad-Diff
source env.sh
```

The terminal should give you some useful information on progress. Please include a copy of the terminal output if you have any issues.

### Command line help

```bash
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

### Usage examples

```bash
# With a Git repo
kidiff led_test.kicad_pcb

# Forcing an specific SCM when more than one is available (Precedence: Git > Fossil > SVN)
kidiff led_test.kicad_pcb --scm fossil

# With a SVN repo, passing commit 1 and 2 on the command line
kidiff led_test.kicad_pcb -a r1 -b r3
```

## Debugging

There should be some output in the launch terminal. Please copy this and include it in any issues posted. If the program is not working, please check that you can run the `plot_kicad_pcb` routine directly by invoking it from the command line and passing the name of the `*.kicad_pcb` file.

```bash
plot_kicad_pcb board.kicad_pcb
```


# Screenshots

<p align="center">
  <img src="https://github.com/Gasman2014/KiCad-Diff/raw/master/docs/gui.png" width="600" alt="Commits Selection GUI">
  <br>
  Commits Selection
  <br>
</p>

<p align="center">
  <img src="https://github.com/Gasman2014/KiCad-Diff/raw/master/docs/gallery.png" width="850" alt="Gallery view">
  <br>
  Gallery View
  <br>
</p>

<p align="center">
  <img src="https://github.com/Gasman2014/KiCad-Diff/raw/master/docs/triptych.png" width="850" alt="Triptych view">
  <br>
  Triptych view
  <br>
</p>


<p align="center">
  <img src="https://github.com/Gasman2014/KiCad-Diff/raw/master/docs/text.png" width="850" alt="Attributes Diff">
  <br>
  Attributes Diff
  <br>
</p>
