# KiCad-Diff
This is a python program with a Tk inteface for comparing KiCad PCB revisions.

The diffing strategy has been changed for this version and SVGs are generated directly rather than doing renderings in ImageMagick as in previous versions. This has made the rendering possible for all layers in a few seconds (compared to 20-60s+ depending on resolution and number of layers selected in previous version). The SVG images are layered together with a different feColorMatrix filter applied to each diff. This highlights areas where features have been added or removed.

The output is presented as a gallery of images of each layer. Each layer pair can be compared and the combined view highlights clearly where the layers differ from each other.

The diff output can be scrolled and zoomed in and out for closer inspection. The pair of 'before and after' views will also pan and zoom together. I have looked at linking all thre windows together but this makes for a very confusing and unsatisfactory effect.

There is an additional 'Text Diff' which is helpful for identifying specif areas which have changed.

This was originaly written as a bash script, this newer GUI version has been rewritten in Python3 and supports Git, SVN and Fossil as SCM tools. I have also removed many of the dependencies.
 

**Instructions**
  *  Check that the paths to your SCM tools are correct (lines 39-45). You do not need to install all of these but if you do not have one, e.g. SVN, make sure that you set svnProg='' etc.
  *  Install 'plotPCB2.py' in /usr/local/bin (or adjust path in lines 45 to suit) This needs to be executable. This program actually generates the necessary SVG files.
  *  Run the main script and select a pair of versions in a source controlled repository from the GUI. The GUI should show which SCM is in use.
  *  The terminal should give you some useful information on progress. Please include a copy of this if you have any issues.
  *  Hit Ctrl + C to terminate the webserver.

  The script should build a series of svg files and display the diff in a webpage. If a web page doesn't open automatically, navigate to "http://127.0.0.1:9090/web/index.html" to view the output. You can adjust the port used (9090 by default) if this conflicts with your existing set-up.
 

***Plans***
  1. Improvement in parsing and meaning of text diffs.
  2. Place all template text/css text in external files.
  3. Improve display of artifacts in diff choice window.
  4. Consider changing GUI elements to wxPython.
  5. Adjust for three pane output to have white outer border & pan-zoom control, not filter colour.
  6. Improve three pane output layout, perhaps with diff tree on LHS and not underneath.
  7. Consider adding 'Preferences' for this program.


***Screenshots***

***GUI***
![GUI](/Documents/gui.png)

![GUI](/Documents/gui2.png)


***Overview***
![Overview](/Documents/Overview.png)


***Main view***
![Main](/Documents/main1.png)

![Main](/Documents/main2.png)


***Diff***
![Fab Layer Diff](/Documents/diff.png)


***Fab Layer***
![Fab layer side by side](/Documents/pair.png)


***F_Cu Layer***
![Cu difference view](/Documents/cu.png)

![Cu layer - 3 pane view](/Documents/composite.png)


***Text Diff***
![Text Diff](/Documents/text.png)