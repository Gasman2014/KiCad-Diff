# KiCad-Diff
Scripts for performing image diffs between pcbnew layout revisions. Extended to show the graphical diff in a webpage.

Based on the initial scripts of spuder and described in  https://github.com/UltimateHackingKeyboard/electronics/tree/master/scripts

The workflow describes how to use a git repository for Kicad printed circuit board board versions. Kicad uses text files for all Whilst it is easy enough to compare a dif between two boards, relying on looking at a text file to determine what has changed is unrewarding.

Additionally, Spuders workflow relied on git - and I rather prefer Fossil-scm as it is a more complete solution (has a wiki and bugtracker built in) and is a small memory footprint.

https://www.fossil-scm.org/index.html/doc/trunk/www/index.wiki

Additionally, spuder's workflow relied on a python script that was downloaded to a /tmp directory. This makes the solution unreliable without internet access.

I have added a web interface to the project. It is functional but needs some beautification.
