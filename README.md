# KiCad-Diff
Scripts for performing image diffs between pcbnew layout revisions. Extended to show the graphical diff in a webpage. Also included some genral Kicad/Fossil observations.

Based on the initial scripts of Spuder and described in  https://github.com/UltimateHackingKeyboard/electronics/tree/master/scripts

The workflow describes how to use a git repository for Kicad printed circuit board board versions. Kicad uses text files for schematic and pcb layout files. Whilst it is easy enough to generate and diff two pcb layout files, the results are almost meningless as it is impossible to decide what items have moved where.

Additionally, Spuders workflow relied on git - and I rather prefer Fossil-scm as it is a more complete solution (has a wiki and bugtracker built in) and is a small memory footprint.

https://www.fossil-scm.org/index.html/doc/trunk/www/index.wiki

Also, Spuder's workflow relied on a python script that was downloaded to a /tmp directory. This makes the solution problematic if you are without internet access.

I have added a web interface to this project. It is functional but needs some work to render it more attractive.

The code is pretty sloppy and fairly sparesly commented but functional. The diff program should be run within a fossil checkout and takes 0, 1 or 2 commit hashes as arguments. With 0 arguments, the script compares the working copy with the last committed version (i.e what has changes since the last commit). With 1 argument, the current checkout is compared to the version identified and with two commit hashes a diff between those versions is calculated.

The diffed versions of the pcb are then used to generate parallel sets of svg files using the kicad python interface. The svg files are then converted to png and cropped to just the board area. Image magick is used to manipulate the images to highlight the changed items.
One strategy is to use the stereo 0 command but I had no luck with this and have come up with an alternative method.

Finally the images are presented in a webpage - clicking an image will bring up a 3-pane diff showing before and after and the composite image with the differences highlighted. The webpage generation code needs a bit of work to make it neater and easier to follow (next part of project).

Kicad tends to modify some of the minor data in the checkout making commits a bit 'noisy'. I have adopted the sheme proposed here https://jnavila.github.io/plotkicadsch/ to ammend the kicad files before commiting them. Although there is quite extensive scripting support in fossil it seems quite difficult to replicate the clean and smudge technique reliably in Fossil. There is a wrapper project called fsl (http://fossil.0branch.com/fsl/home) which acts as an interceptor to fossil commands and, additionally offers some extra shortcuts and some more colourful logging options (and the Dresden branch allows the use of simple revision numbers). The behavior is controlled by a ~/.fslrc file which I have included in this repo. 

I am running this setup on macOs 10.12 but I would imagine any linux varient would work as well. Windows - ymmv...

Dependencies
  *  gsed (Mac sed is limited)
  *  Kicad with python scripting enabled
  *  Image Magick
  *  Fossil scm
  *  Possibly some others but all have been installed with the help of brew
  
  ## screenshots
Overview
![screenshot overview](/Documents/Overview.png)

Three panel view
![screenshot Three panel view](/Documents/3panel.png)

Detail
![screenshot Detail1] (/Documents/F_Cu.png)

Detail
![screenshot Detail2] (/Documents/F_Cu2.png)

Detail
![screenshot Detail3] (/Documents/F_Fab.png)

Detail
![screenshot Detail4] (/Documents/F_Mask.png)

