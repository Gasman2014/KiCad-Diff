#!/usr/bin/env python3
#
# A python script to select two revisions of a Kicad pcbnew layout
# held in a suitable version control repository and produce a graphical diff
# of generated svg files in a web browser.

# TODO [ ] Place all template text/css text in external files.
# TODO [ ] Improve display of artifacts in diff choice window.
# TODO [ ] Consider changing GUI elements to wxPython.
# TODO [*] Manage any missing SCM paths - reflect available SCM progs in splash screen.
# TODO [ ] Adjust <div> for three pane output to have white outer border & pan-zoom control, not filter colour.
# TODO [ ] Improve three pane output layout, perhaps with diff tree on LHS and not underneath.

# DEBUG Tk window not being destroyed when closed.
# DEBUG Minor error with parsing FP_Text diff.

import os
import time
import subprocess
import tkinter as tk
import webbrowser
from subprocess import PIPE, STDOUT, Popen
from tkinter import *
from tkinter import filedialog, ttk
from tkinter.messagebox import showinfo
import tkUI
from tkUI import *
import http.server
import socketserver
socketserver.TCPServer.allow_reuse_address = True

import argparse

if sys.version_info[0] >= 3:
    unicode = str

executablePath = os.path.dirname(os.path.realpath(__file__))

def _escape_string( val ):
    # Make unicode
    val = unicode( val )
    # Escape stuff
    val = val.replace( u'\\', u'\\\\' )
    val = val.replace( u' ', u'\\ ' )
    return ''.join(val.splitlines())

# -------------------------------------------------------------------------

# Tools should be on the PATH
# Much more flexible approach
# To add plotPCB.py, kidiff_linux.py and kidiff_gui.py to the path use the following example
# Example: source ./env.sh
gitProg = 'git'
fossilProg = 'fossil'
svnProg = 'svn'
diffProg = 'diff'
grepProg = 'grep'
plotProg = 'plotPCB.py'

plotDir = '/plots'
webDir = '/web'

# -------------------------------------------------------------------------
# NOTE Please adjust these colours to suit your requirements.

layerCols = {
    'F_Cu': "#952927",
    'B_Cu': "#359632",
    'B_Paste': "#3DC9C9",
    'F_Paste': "#969696",
    'F_SilkS': "#339697",
    'B_SilkS': "#481649",
    'B_Mask': "#943197",
    'F_Mask': "#943197",
    'Edge_Cuts': "#C9C83B",
    'Margin': "#D357D2",
    'In1_Cu': "#C2C200",
    'In2_Cu': "#C200C2",
    'Dwgs_User': "#0364D3",
    'Cmts_User': "#7AC0F4",
    'Eco1_User': "#008500",
    'Eco2_User': "#C2C200",
    'B_Fab': "#858585",
    'F_Fab': "#C2C200",
    'B_Adhes': "#3545A8",
    'F_Adhes': "#A74AA8",
    'B_CrtYd': "#D3D04B",
    'F_CrtYd': "#A7A7A7",
}

Handler = http.server.SimpleHTTPRequestHandler


# ------------------------------------------HTML Template Blocks-------------------------------------------
#
# FIXME These should go into external files to clean up and seperate the code


tail = '''
<div class="clearfix"></div>
<div style="padding:6px;"></div>
'''

indexHead = '''
<!DOCTYPE HTML>
<html lang="en">
<meta charset="utf-8" /> 
<head>
    <link rel="stylesheet" type="text/css" href="style.css" media="screen" />
</head>
<div class="responsivefull">
    <table style="border-color: #aaaaaa; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">
        <tbody>
            <tr>
                <td colspan="3" rowspan="3" width="45%">
                    <div class="title"> Title: {TITLE} </div>
                    <div class="details"> Company: {COMPANY} </div>
                </td>
                <td width="25%">
                    <div class="versions">Thickness (mm)</div>
                </td>
                <td width="15%">
                    <div class="versions green">{THICK1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{THICK2}</div>
                </td>
            </tr>
            <td width="25%">
                <div class="versions">Modules</div>
            </td>
            <td width="15%">
                <div class="versions green">{MODULES1}</div>
            </td>
            <td width="15%">
                <div class="versions red">{MODULES2}</div>
            </td>
            <tr>
                <td width="25%">
                    <div class="versions">Drawings</div>
                </td>
                <td width="15%">
                    <div class="versions green">{DRAWINGS1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{DRAWINGS2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Version</div>
                </td>
                <td width="15%">
                    <div class="versions green">{diffDir1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{diffDir2}</div>
                </td>
                <td width="25%">
                    <div class="versions">Nets</div>
                </td>
                <td width="15%">
                    <div class="versions green">{NETS1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{NETS2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Date</div>
                </td>
                <td width="15%">
                    <div class="versions">{D1DATE}</div>
                </td>
                <td width="15%">
                    <div class="versions">{D2DATE}</div>
                </td>
                <td width="25%">
                    <div class="versions">Tracks</div>
                </td>
                <td width="15%">
                    <div class="versions green">{TRACKS1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{TRACKS2}</div>
                </td>
            </tr>
            <tr>
                <td width="15%">
                    <div class="versions">Time</div>
                </td>
                <td width="15%">
                    <div class="versions">{D1TIME}</div>
                </td>
                <td width="15%">
                    <div class="versions">{D2TIME}</div>
                </td>
                <td width="25%">
                    <div class="versions">Zones</div>
                </td>
                <td width="15%">
                    <div class="versions green">{ZONES1}</div>
                </td>
                <td width="15%">
                    <div class="versions red">{ZONES2}</div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
'''

outfile = '''
<div class="responsive">
  <div class="gallery">
    <a target="_blank" href=../{diff1}/{layername}>
    <a href=./tryptych/{prj}-{layer}.html> <img class="{layer}" src=../{diff1}/{layername} height="200"> </a>
    </a>
    <div class="desc">{layer}</div>
  </div>
</div>
'''

tryptychHTML = '''
<!DOCTYPE HTML>
<html lang="en">
<meta charset="utf-8" /> 
<head>
<link rel="stylesheet" type="text/css" href="../style.css" media="screen" />
<style>
div.responsive {{
   padding: 0 6px;
   float: left;
   width: 49.99%;
   }}
</style>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.0/dist/svg-pan-zoom.min.js"></script>
</head>
<body>
<div class="title">{prj}</div>
<div class="subtitle">{layer}</div>


     <div id="compo-container" style="width: 100%; height: 800px;">
        <svg id="svg-id" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: inherit; min-width: inherit; max-width: inherit; height: inherit; min-height: inherit; max-height: inherit;" version="1.1">
            <g>
                <svg id="compo">
                    <defs>
                        <filter id="f1">
                            <feColorMatrix id="c1" type="matrix" values="1   0   0   0   0
                  0   1   0   1   0
                  0   0   1   1   0
                  0   0   0   1   0 " />
                        </filter>
                    </defs>
                    <image x="0" y="0" height="100%" width="100%" filter="url(#f1)" xlink:href="../../{diff1}/{layername}" />
                </svg>

                <svg id="compo2">
                    <defs>
                        <filter id="f2">
                            <feColorMatrix id="c2" type="matrix" values="1   0   0   1   0
                  0   1   0   0   0
                  0   0   1   0   0
                  0   0   0   .5   0" />
                        </filter>
                    </defs>
                    <image x="0" y="0" height="100%" width="100%" filter="url(#f2)" xlink:href="../../{diff2}/{layername}" />
                </svg>
            </g>
        </svg>
    </div>

<div id="sbs-container"  width=100%; height=100% >
<embed id="diff1" class="{layer}" type="image/svg+xml" style="width: 50%; float: left; border:1px solid black;" src="../../{diff1}/{layername}" />
<embed id="diff2" class="{layer}" type="image/svg+xml" style="width: 50%; border:1px solid black;" src="../../{diff2}/{layername}" />
</div>

'''

twopane='''
<script>
        // Don't use window.onLoad like this in production, because it can only listen to one function.
        window.onload = function() {
            // Expose variable for testing purposes
            window.panZoomDiff = svgPanZoom('#svg-id', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                center: true,
                minZoom: 1.5,
                maxZoom: 20,
            });
            // Expose variable to use for testing
            window.zoomDiff = svgPanZoom('#diff1', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                minZoom: 1.5,
                maxZoom: 20,
                // Uncomment this in order to get Y asis synchronized pan
                // beforePan: function(oldP, newP) {return {y:false}},
            });

            // Expose variable to use for testing
            window.zoomDiff2 = svgPanZoom('#diff2', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                minZoom: 1.5,
                maxZoom: 20,
            });

            zoomDiff.setOnZoom(function(level) {
                zoomDiff2.zoom(level)
                zoomDiff2.pan(zoomDiff.getPan())
            })

            zoomDiff.setOnPan(function(point) {
                zoomDiff2.pan(point)
            })

            zoomDiff2.setOnZoom(function(level) {
                zoomDiff.zoom(level)
                zoomDiff.pan(zoomDiff2.getPan())
            })

            zoomDiff2.setOnPan(function(point) {
                zoomDiff.pan(point)
            })

        };
</script>

</body>

</html>
'''

css = '''
body {
    background-color: #2c3031;
    margin: 0 auto;
    max-width: 45cm;
    border: 1pt solid #586e75;
    padding: 0.5em;
}

table {
    border-collapse: collapse;
    border-spacing: 0;
    border-color: #e2e3e3;
    width: 100%; 
    height: 2px;
    border: 2px 
}

html {
    background-color: #222222;
    color: #e2e3e3;
    margin: 1em;
}

.tabbed {
    float: left;
    width: 100%;
    padding: 0 6px;
}

.tabbed>input {
    display: none;
}

.tabbed>section>h1 {
    font: 14px arial, sans-serif;
    float: left;
    box-sizing: border-box;
    margin: 0;
    padding: 0.5em 0.1em 0;
    overflow: hidden;
    font-size: 1em;
    font-weight: normal;
}

.tabbed>input:first-child+section>h1 {
    padding-left: 1em;
}

.tabbed>section>h1>label {
    font: 14px arial, sans-serif;
    display: block;
    padding: 0.25em 0.75em;
    border: 1px solid #ddd;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    box-shadow: 0 0 0.5em rgba(0, 0, 0, 0.0625);
    background: rgb(50, 50, 50);
    cursor: pointer;
}

.tabbed>section>div {
    position: relative;
    z-index: 1;
    float: right;
    box-sizing: border-box;
    width: 100%;
    margin: 1.95em 0 0 -100%;
    padding: 0.25em 0.75em;
    border: 1px solid #ddd;

    box-shadow: 0 0 1em rgb(245, 245, 245);
    background: rgba(70, 67, 67, 0.185);
}

.tabbed>input:checked+section>h1 {
    position: relative;
    z-index: 2;
    border-bottom: none;
}


.tabbed>input:not(:checked)+section>div {
    display: none;
}

a:active,
a:hover {
    outline: 0;
}


.gallery {
    border: 1px solid #ccc;
    background-color: #222;
    padding: 5px;
    align: middle;
    vertical-align: middle;
}

.gallery:hover {
    border: 1px solid #777;
}

.gallery img {
    width: 100%;
    height: auto;
}

.desc,
.title {
    padding: 10px;
    text-align: center;
    font: 12px arial, sans-serif;
}

.title,
.subtitle,
.details {
    padding-left: 10px;
    text-align: left;
    font: 20px arial, sans-serif;
    color: #dddddd;
}

.subtitle {
    font: 14px arial, sans-serif;
}

.details,
.versions {
    padding: 5px;
    font: 12px arial, sans-serif;
    padding-bottom: 5px;
}


.differences {
    font: 12px courier, monospace;
    padding: 5px;
}

* {
    box-sizing: border-box;
}

.responsive {
    padding: 0 6px;
    float: left;
    width: 19.99999%;
    margin: 6px 0;
}

@media only screen and (max-width:700px) {
    .responsive {
        width: 49.98%;
        margin: 6px 0;
    }
}

@media only screen and (max-width:500px) {
    .responsive {
        width: 100%;
        margin: 6px 0;
    }
}

.responsivefull {
    padding: 0 6px;
    width: 100%;
    margin: 3px 0;
}

.clearfix:after {
    content: "";
    display: table;
    clear: both;
}

.box {
    float: left;
    width: 20px;
    height: 20px;
    margin: 5px;
    border: 1px solid rgba(0, 0, 0, .2);
}

.red {
    background: #832320;
}

.green {
    background: #44808aa8;
}


.added {
    color: #5eb6c4;
    text-align: left;
}

.removed {
    color: #ba312d;
    text-align: right;
}

.tbr td {
    color:#ba312d;
    padding: 10px;
    font: 12px arial,sans-serif;
    padding-bottom: 5px;
}

.tbl td {
    color: #5eb6c4;
    padding: 10px;
    font: 12px arial, sans-serif;
    padding-bottom: 5px;
}

.tbr th {
    text-align: left;
    background: #832320;
    padding: 10px;
    font: 12px arial, sans-serif;
    font-weight: bold;
    padding-bottom: 5px;
}

.tbl th {
    text-align: left;
    background: #44808aa8;
    padding: 10px;
    font: 12px arial, sans-serif;
    font-weight: bold;
    padding-bottom: 5px;
}

.F_Cu {
    filter: invert(28%) sepia(50%) saturate(2065%) hue-rotate(334deg) brightness(73%) contrast(97%);
}

.B_Cu {
    filter: invert(44%) sepia(14%) saturate(2359%) hue-rotate(70deg) brightness(103%) contrast(82%);
}

.B_Paste {
    filter: invert(91%) sepia(47%) saturate(4033%) hue-rotate(139deg) brightness(82%) contrast(91%);
}

.F_Paste {
    filter: invert(57%) sepia(60%) saturate(6%) hue-rotate(314deg) brightness(92%) contrast(99%);
}

.F_SilkS {
    filter: invert(46%) sepia(44%) saturate(587%) hue-rotate(132deg) brightness(101%) contrast(85%);
}

.B_SilkS {
    filter: invert(14%) sepia(27%) saturate(2741%) hue-rotate(264deg) brightness(95%) contrast(102%);
}

.B_Mask {
    filter: invert(22%) sepia(56%) saturate(2652%) hue-rotate(277deg) brightness(94%) contrast(87%);
}

.F_Mask {
    filter: invert(27%) sepia(51%) saturate(1920%) hue-rotate(269deg) brightness(89%) contrast(96%);
}

.Edge_Cuts {
    filter: invert(79%) sepia(79%) saturate(401%) hue-rotate(6deg) brightness(88%) contrast(88%);
}

.Margin {
    filter: invert(74%) sepia(71%) saturate(5700%) hue-rotate(268deg) brightness(89%) contrast(84%);
}

.In1_Cu {
    filter: invert(69%) sepia(39%) saturate(1246%) hue-rotate(17deg) brightness(97%) contrast(104%);
}

.In2_Cu {
    filter: invert(14%) sepia(79%) saturate(5231%) hue-rotate(293deg) brightness(91%) contrast(119%);
}

.Dwgs_User {
    filter: invert(40%) sepia(68%) saturate(7431%) hue-rotate(203deg) brightness(89%) contrast(98%);
}

.Cmts_User {
    filter: invert(73%) sepia(10%) saturate(1901%) hue-rotate(171deg) brightness(95%) contrast(102%);
}

.Eco1_User {
    filter: invert(25%) sepia(98%) saturate(2882%) hue-rotate(109deg) brightness(90%) contrast(104%);
}

.Eco2_User {
    filter: invert(85%) sepia(21%) saturate(5099%) hue-rotate(12deg) brightness(91%) contrast(102%);
}

.B_Fab {
    filter: invert(60%) sepia(0%) saturate(0%) hue-rotate(253deg) brightness(87%) contrast(90%);
}

.F_Fab {
    filter: invert(71%) sepia(21%) saturate(4662%) hue-rotate(21deg) brightness(103%) contrast(100%);
}

.B_Adhes {
    filter: invert(24%) sepia(48%) saturate(2586%) hue-rotate(218deg) brightness(88%) contrast(92%);
}

.F_Adhes {
    filter: invert(38%) sepia(49%) saturate(1009%) hue-rotate(254deg) brightness(88%) contrast(86%);
}

.B_CrtYd {
    filter: invert(79%) sepia(92%) saturate(322%) hue-rotate(3deg) brightness(89%) contrast(92%);
}

.F_CrtYd {
    filter: invert(73%) sepia(1%) saturate(0%) hue-rotate(116deg) brightness(92%) contrast(91%);
}
'''

# ----------------------Main Functions begin here---------------------------------------
# 

def getGitPath(prjctName, prjctPath):
    gitRootCmd = 'cd ' + prjctPath + ' && ' + gitProg + ' rev-parse --show-toplevel'

    gitRootProcess = Popen(
        gitRootCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = gitRootProcess.communicate()

    gitRoot = stdout.decode('utf-8')

    gitPathCmd = 'cd ' + _escape_string(gitRoot) + ' && ' + gitProg + ' ls-tree -r --name-only HEAD | ' + grepProg + ' -m 1 ' + prjctName

    gitPathProcess = Popen(
        gitPathCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = gitPathProcess.communicate()

    gitPathProcess.wait()

    return _escape_string(stdout.decode('utf-8'))

def getGitDiff(diff1, diff2, prjctName, prjctPath):
    '''Given two git artifacts, write out two kicad_pcb files to their respective
    directories (named after the artifact). Returns the date and time of both commits'''

    artifact1 = diff1[:6]
    artifact2 = diff2[:6]

    findDiff = 'cd ' + _escape_string(prjctPath) + ' && ' + gitProg + ' diff --name-only ' + \
        artifact1 + ' ' + artifact2 + ' | ' + grepProg + ' .kicad_pcb'

    changes = Popen(
        findDiff,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = changes.communicate()
    changes.wait()
    changed = (stdout.decode('utf-8'))

    if changed == '':
        print("No .kicad_pcb files differ between these commits")
        sys.exit()

    outputDir1 = prjctPath + plotDir + '/' + artifact1
    outputDir2 = prjctPath + plotDir + '/' + artifact2

    if not os.path.exists(outputDir1):
        os.makedirs(outputDir1)

    if not os.path.exists(outputDir2):
        os.makedirs(outputDir2)

    gitPath = getGitPath(prjctName, _escape_string(prjctPath))

    gitArtifact1 = 'cd ' + _escape_string(prjctPath) + ' && ' + gitProg + ' show ' + artifact1 + \
        ':' + gitPath + ' > ' + _escape_string(outputDir1) + '/' + prjctName

    gitArtifact2 = 'cd ' + _escape_string(prjctPath) + ' && ' + gitProg + ' show ' + artifact2 + \
        ':' + gitPath + ' > ' + _escape_string(outputDir2) + '/' + prjctName

    ver1 = Popen(
        gitArtifact1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = ver1.communicate()

    ver2 = Popen(
        gitArtifact2,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = ver2.communicate()

    ver1.wait(); ver2.wait()

    gitDateTime1 = 'cd ' + _escape_string(prjctPath) + ' && ' + gitProg + ' show -s --format="%ci" ' + artifact1
    gitDateTime2 = 'cd ' + _escape_string(prjctPath) + ' && ' + gitProg + ' show -s --format="%ci" ' + artifact2

    print(gitDateTime1,gitDateTime2)

    dt1 = Popen(
        gitDateTime1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = dt1.communicate()
    dt1.wait()


    dateTime1 = stdout.decode('utf-8')
    date1, time1, UTC = dateTime1.split(' ')

    dt2 = Popen(
        gitDateTime2,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = dt2.communicate()
    dt2.wait()

    dateTime2 = stdout.decode('utf-8')
    date2, time2, UTC = dateTime2.split(' ')

    times = date1 + " " + time1 + " " + date2 + " " + time2
    print(times)
    return (times)


def getSVNDiff(diff1, diff2, prjctName, prjctPath):
    '''Given two SVN revisions, write out two kicad_pcb files to their respective
    directories (named after the revision number). Returns the date and time of both commits'''

    svnChanged = 'cd ' + prjctPath + ' && svn diff --summarize -r ' + \
        diff1 + ':' + diff2 + ' ' + prjctName

    changed = Popen(
        svnChanged,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = changed.communicate()
    changed.wait()

    changed, *boardName = (stdout.decode('utf-8'))

    if changed != 'M':
        print("No .kicad_pcb files differ between these commits")
        sys.exit()

    outputDir1 = prjctPath + plotDir + '/' + diff1
    outputDir2 = prjctPath + plotDir + '/' + diff2

    if not os.path.exists(outputDir1):
        os.makedirs(outputDir1)

    if not os.path.exists(outputDir2):
        os.makedirs(outputDir2)

    SVNdiffCmd1 = 'cd ' + prjctPath + ' && svn cat -r ' + diff1 + \
        " " + prjctName + ' > ' + outputDir1 + '/' + prjctName
    SVNdiffCmd2 = 'cd ' + prjctPath + ' && svn cat -r ' + diff2 + \
        " " + prjctName + ' > ' + outputDir2 + '/' + prjctName

    ver1 = Popen(
        SVNdiffCmd1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = ver1.communicate()

    ver2 = Popen(
        SVNdiffCmd2,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = ver2.communicate()

    ver1.wait(); ver2.wait()

    dateTime1 = 'cd ' + prjctPath + ' && svn log -r' + diff1
    dateTime2 = 'cd ' + prjctPath + ' && svn log -r' + diff2

    dt1 = Popen(
        dateTime1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = dt1.communicate()

    dt1.wait()
    dateTime = stdout.decode('utf-8')
    cmt = (dateTime.splitlines()[1]).split('|')
    _, SVNdate1, SVNtime1, SVNutc, *_ = cmt[2].split(' ')

    dt2 = Popen(
        dateTime2,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = dt2.communicate()
    dt2.wait()
    dateTime = stdout.decode('utf-8')
    cmt = (dateTime.splitlines()[1]).split('|')
    _, SVNdate2, SVNtime2, SVNutc, *_ = cmt[2].split(' ')

    times = SVNdate1 + " " + SVNtime1 + " " + SVNdate2 + " " + SVNtime2

    print(times)

    return (times)


def getFossilDiff(diff1, diff2, prjctName, prjctPath):
    '''Given two Fossil artifacts, write out two kicad_pcb files to their respective
    directories (named after the artifacts). Returns the date and time of both commits'''

    artifact1 = diff1[:6]
    artifact2 = diff2[:6]

    findDiff = 'cd ' + _escape_string(prjctPath) + ' && fossil diff --brief -r ' + \
        artifact1 + ' --to ' + artifact2 + ' | ' + grepProg + ' .kicad_pcb'

    changes = Popen(
        findDiff,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = changes.communicate()
    changes.wait()

    changed = (stdout.decode('utf-8'))
    print(changed)
    if changed == '':
        print("No .kicad_pcb files differ between these commits")
        sys.exit()

    outputDir1 = prjctPath + plotDir + '/' + artifact1
    outputDir2 = prjctPath + plotDir + '/' + artifact2

    if not os.path.exists(outputDir1):
        os.makedirs(outputDir1)

    if not os.path.exists(outputDir2):
        os.makedirs(outputDir2)

    fossilArtifact1 = 'cd ' + _escape_string(prjctPath) + ' && fossil cat ' + _escape_string(prjctPath) + '/' + prjctName + \
        ' -r ' + artifact1 + ' > ' + outputDir1 + '/' + prjctName
    fossilArtifact2 = 'cd ' + _escape_string(prjctPath) + ' && fossil cat ' + _escape_string(prjctPath) + '/' + prjctName + \
        ' -r ' + artifact2 + ' > ' + outputDir2 + '/' + prjctName

    fossilInfo1 = 'cd ' + _escape_string(prjctPath) + ' && fossil info ' + artifact1
    fossilInfo2 = 'cd ' + _escape_string(prjctPath) + ' && fossil info ' + artifact2

    ver1 = Popen(
        fossilArtifact1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = ver1.communicate()
    ver1.wait()

    info1 = Popen(
        fossilInfo1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = info1.communicate()
    info1.wait()

    dateTime = stdout.decode('utf-8')
    dateTime = dateTime.strip()
    uuid, _, _, _, _, _, _, _, _, artifactRef, dateDiff1, timeDiff1, *junk1 = dateTime.split(
        " ")

    ver2 = Popen(
        fossilArtifact2,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = ver2.communicate()
    ver2.wait()

    info2 = Popen(
        fossilInfo2,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = info2.communicate()
    info2.wait()

    dateTime = stdout.decode('utf-8')
    dateTime = dateTime.strip()
    uuid, _, _, _, _, _, _, _, _, artifactRef, dateDiff2, timeDiff2, *junk1 = dateTime.split(
        " ")

    dateTime = dateDiff1 + " " + timeDiff1 + " " + dateDiff2 + " " + timeDiff2

    print(dateTime)

    return dateTime


def getProject():
    '''File select dialogue. Opens Tk File browser and 
    selector set for .kicad_pcb files. Returns path and file name
    '''
    selected = tk.filedialog.askopenfile(
        initialdir="~/",
        title="Select kicad_pcb file in a VC directory",
        filetypes=(("KiCad pcb files", "*.kicad_pcb"), ("all files", "*.*")))
    if selected:
        path, prjct = os.path.split(selected.name)

    return (path, prjct)


def getSCM(prjctPath):
    '''Determines which SCM methodology is in place when passed the enclosing
    directory. NB there is no facility to deal with directories with multiple VCS in place
    and current order of priority is Git > Fossil > SVN.
    Easy to add additional SCMs but also would need to write handling code
    '''

    scm = ''

    # check if SVN program installed and then check if *.kicad_pcb is in a SVN checkout
    if (svnProg != ''):
        svnCmd = 'cd ' + prjctPath + ' && ' + svnProg + ' log | perl -l4svn log0pe "s/^-+/\n/"'
        svn = Popen(
            svnCmd,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            close_fds=True)
        stdout, stderr = svn.communicate()
        svn.wait()
        if ((stdout.decode('utf-8') != '') & (stderr.decode('utf-8') == '')):
            scm = 'SVN'

    # check if Fossil program installed and then check if *.kicad_pcb is in a Fossil checkout
    if (fossilProg != ''):
        fossilCmd = 'cd ' + prjctPath + ' && ' + fossilProg + ' status'
        fossil = Popen(
            fossilCmd,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            close_fds=True)
        stdout, stderr = fossil.communicate()
        fossil.wait()
        # print(stdout.decode('utf-8'),"stdERROR=", stderr.decode('utf-8'))
        if (stdout.decode('utf-8') != ''):
            scm = 'Fossil'

    # Check if Git program installed and then check if *.kicad_pcb is in a Git checkout
    if (gitProg != ''):
        gitCmd = 'cd ' + prjctPath + ' && ' + gitProg + ' status'
        git = Popen(
            gitCmd,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            close_fds=True)
        stdout, stderr = git.communicate()
        git.wait()
        if ((stdout.decode('utf-8') != '') & (stderr.decode('utf-8') == '')):
            scm = 'Git'

    return scm


def fossilDiff(path, kicadPCB):
    '''Returns list of Fossil artifacts from a directory containing a
    *.kicad_pcb file.'''

    # NOTE Assemble a list of artefacts. Unfortunatly, Fossil doesn't give any easily configurable length.
    # NOTE Using the -W option results in multiline diffs
    # NOTE 'fossil -finfo' looks like this
    # 2017-05-19 [21d331ea6b] Preliminary work on CvPCB association and component values (user: johnpateman, artifact: [1100d6e077], branch: Ver_3V3)
    # 2017-05-07 [2d1e20f431] Initial commit (user: johnpateman, artifact: [24336219cc], branch: trunk)
    # NOTE 'fossil -finfo -b' looks like this
    # 21d331ea6b 2017-05-19 johnpate Ver_3V3 Preliminary work on CvPCB association a
    # 2d1e20f431 2017-05-07 johnpate trunk Initial commit
    # TODO Consider parsing the output of fossil finfo and split off date, artifactID, mesage, user and branch

    fossilCmd = 'cd ' + path + ' && ' + fossilProg + ' finfo -b ' + kicadPCB

    fossil = Popen(
        fossilCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, _ = fossil.communicate()
    fossil.wait()
    line = (stdout.decode('utf-8').splitlines())
    # fArtifacts = [a.replace(' ', '       ', 4) for a in line]
    fArtifacts = [a.replace(' ', '\t', 4) for a in line]
    return fArtifacts


def gitDiff(path, kicadPCB):
    '''Returns list of Git artifacts from a directory containing a
    *.kicad_pcb file.'''

    gitCmd = 'cd ' + path + ' && ' + gitProg + ' log --pretty=format:"%h \t %s"'
    git = Popen(
        gitCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, _ = git.communicate()
    git.wait()
    gArtifacts = (stdout.decode('utf-8').splitlines())
    return gArtifacts


def svnDiff(path, kicadPCB):
    '''Returns list of SVN resvisions from a directory containing a
    *.kicad_pcb file.'''
    svnCmd = 'cd ' + path + ' && ' + svnProg + ' log -r HEAD:0 | perl -l40pe "s/^-+/\n/"'

    svn = Popen(
        svnCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = svn.communicate()
    svn.wait()
    sArtifacts = (stdout.decode('utf-8').splitlines())
    sArtifacts = list(filter(None, sArtifacts))
    return sArtifacts


def makeSVG(d1, d2, prjctName, prjctPath):
    '''Hands off required .kicad_pcb files to "plotPCB2.py"
    and generate .svg files. Routine is
    v quick so all layers are plotted to svg.'''

    print("Generating .svg files")

    d1 = d1[:6]
    d2 = d2[:6]

    Diff1 = prjctPath + plotDir + '/' + d1 + '/' + prjctName
    Diff2 = prjctPath + plotDir + '/' + d2 + '/' + prjctName

    d1SVG = prjctPath + plotDir + '/' + d1
    d2SVG = prjctPath + plotDir + '/' + d2

    if not os.path.exists(d1SVG):
        os.makedirs(d1SVG)
    if not os.path.exists(d2SVG):
        os.makedirs(d2SVG)

    plot1Cmd = plotProg + ' ' + _escape_string(Diff1) + ' ' + _escape_string(d1SVG)
    plot2Cmd = plotProg + ' ' + _escape_string(Diff2) + ' ' + _escape_string(d2SVG)

    plot1=Popen(
        plot1Cmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = plot1.communicate()
    plotDims1 = (stdout.decode('utf-8').splitlines())
    errors = stderr.decode('utf-8')
    if errors != "":
        print("Plot1 error: " + errors)

    plot2=Popen(
        plot2Cmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = plot2.communicate()
    plotDims2 = (stdout.decode('utf-8').splitlines())
    errors = stderr.decode('utf-8')
    if errors != "":
        print("Plot2 error: " + errors)

    plot1.wait(); plot2.wait()


    return (d1, d2, plotDims1[0], plotDims2[0])


def makeSupportFiles(prjctName, prjctPath):
    '''
    Setup web directories for output
    '''

    webd = prjctPath + plotDir + webDir
    webIndex = webd + '/index.html'
    webStyle = webd + '/style.css'

    if not os.path.exists(webd):
        os.makedirs(webd)
        os.makedirs(webd + '/tryptych')

    makeCSS = open(webStyle, 'w')
    makeCSS.write(css)

    if os.path.exists(webIndex):
        os.remove(webIndex)

    return

def getBoardData(board):
    '''Takes a board reference and returns the
    basic parameters from it.
    Might be safer to split off the top section
    before the modules to avoid the possibility of
    recyling keywords like 'title' '''

    prms = {
        'title': "",
        'rev': "",
        'company': "",
        'date': "",
        'page': "",
        'thickness': 0,
        'drawings': 0,
        'tracks': 0,
        'zones': 0,
        'modules': 0,
        'nets': 0
    }

    thickDone = False

    with open(board, 'r') as f:
        for line in f:
            words = line.strip("\t ()").split()
            for key in prms:
                if len(words) > 1:
                    if key == words[0]:
                        complete =""
                        for i in range(1,len(words)):
                            complete += words[i].strip("\t ()").replace("\"","") + " "
                        prms[key] = complete
    print(prms)
    return(prms)

def makeOutput(diffDir1, diffDir2, prjctName, prjctPath, times, dim1, dim2):
    '''Write out HTML using template. Iterate through files in diff directories, generating
    thumbnails and three way view (tryptych) page.
    '''
    webd = prjctPath + plotDir + webDir

    board1 = prjctPath + plotDir + "/" + diffDir1 + "/" + prjctName
    board2 = prjctPath + plotDir + "/" + diffDir2 + "/" + prjctName

    webIndex = webd + '/index.html'

    webOut = open(webIndex, 'w')

    D1DATE, D1TIME, D2DATE, D2TIME = times.split(" ")

    board_1_Info = getBoardData(board1)
    board_2_Info = getBoardData(board2)

    TITLE = board_1_Info.get('title')
    DATE = board_1_Info.get('date')
    COMPANY = board_1_Info.get('company')

    THICK1 = board_1_Info.get('thickness')
    DRAWINGS1 = board_1_Info.get('drawings')
    TRACKS1 = board_1_Info.get('tracks')
    ZONES1 = board_1_Info.get('zones')
    MODULES1 = board_1_Info.get('modules')
    NETS1 = board_1_Info.get('nets')

    THICK2 = board_2_Info.get('thickness')
    DRAWINGS2 = board_2_Info.get('drawings')
    TRACKS2 = board_2_Info.get('tracks')
    ZONES2 = board_2_Info.get('zones')
    MODULES2 = board_2_Info.get('modules')
    NETS2 = board_2_Info.get('nets')


    index=indexHead.format(
    TITLE=TITLE,
    DATE=DATE,
    COMPANY=COMPANY,
    diffDir1=diffDir1,
    diffDir2=diffDir2,
    THICK1=THICK1,
    THICK2=THICK2,
    D1DATE=D1DATE,
    D2DATE=D2DATE,
    DRAWINGS1=DRAWINGS1,
    DRAWINGS2=DRAWINGS2,
    D1TIME=D1TIME,
    D2TIME=D2TIME,
    TRACKS1=TRACKS1,
    TRACKS2=TRACKS2,
    ZONES1=ZONES1,
    ZONES2=ZONES2,
    MODULES1=MODULES1,
    MODULES2=MODULES2,
    NETS1=NETS1,
    NETS2=NETS2,
    )

    webOut.write(index)

    diffCmnd1 = ()

    source = prjctPath + plotDir + "/" + diffDir1 + "/"

    tryptychDir = prjctPath + plotDir + webDir + '/tryptych'

    if not os.path.exists(tryptychDir):
        os.makedirs(tryptychDir)

    # diffs = os.fsencode(source)

    for f in os.listdir(source):
        filename = os.fsdecode(f)
        if filename.endswith(".svg"):
            print(filename)
            file, file_extension = os.path.splitext(filename)
            tryptych = tryptychDir + '/' + file + '.html'
            *project, layer = filename.split('-')
            layer, ext = layer.split('.')
            prjct, ext = filename.split('.')
            # Accounts for project names containing hyphens
            splitted = prjct.split('-')
            prj = splitted[-2]
            layer = splitted[-1]
            out=outfile.format(
                diff1=diffDir1,
                diff2=diffDir2,
                dim1=dim1,
                dim2=dim2,
                layer=layer,
                layername=filename,
                prj=prj)

            webOut.write(out)

            tryptychOut = open(tryptych, 'w')

            t_out = tryptychHTML.format(
                layername=filename,
                diff1=diffDir1,
                diff2=diffDir2,
                dim1=dim1,
                dim2=dim2,
                plotDir=plotDir,
                layer=layer,
                prj=prj)

            tryptychOut.write(t_out)

            diffbase=diffProg+'{prjctPath}{plotDir}/{diff2}/*.kicad_pcb {prjctPath}{plotDir}/{diff1}/*.kicad_pcb >> {prjctPath}{plotDir}/diff.txt'

            if not diffCmnd1:
                diffCmnd1 = diffbase.format(
                    plotDir=plotDir,
                    diff1=diffDir1,
                    diff2=diffDir2,
                    prjctPath=_escape_string(prjctPath))
                # print(diffCmnd1)

                diff1Txt = Popen(
                    diffCmnd1,
                    shell=True,
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    close_fds=True)
                stdout, stderr = diff1Txt.communicate()
                diff1Txt.wait()
            #sed -e 's/(layer {mod}*)//g' |
            mod = layer.replace("_",".")
            #            diffCmnd2 = diffProg + ''' --suppress-common-lines {prjctPath}{plotDir}/{diff2}/*.kicad_pcb {prjctPath}{plotDir}/{diff1}/*.kicad_pcb | grep {mod} | sed 's/>  /<\/div><div class="differences added">/g' | sed 's/<   /<\/div><div class="differences removed">/g' | sed 's/\/n/<\/div>/g' | sed 's/(status [1-9][0-9])//g' '''.format(
            diffCmnd2 = diffProg + ''' --suppress-common-lines {prjctPath}{plotDir}/{diff2}/*.kicad_pcb {prjctPath}{plotDir}/{diff1}/*.kicad_pcb | {grepProg} {mod} | sed 's/(status [1-9][0-9])//g' '''.format(
                layername=filename,
                plotDir=plotDir,
                diff1=diffDir1,
                diff2=diffDir2,
                prjctPath=_escape_string(prjctPath),
                mod=mod,
                grepProg=grepProg,
                webDir=webDir)


            diff2Txt = Popen(
                    diffCmnd2,
                    shell=True,
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    close_fds=True)
            stdout, stderr = diff2Txt.communicate()
            diff2Txt.wait()
            out = stdout.decode('utf8')

            processed = processDiff(out, mod)
            processed+=twopane

            tryptychOut.write(processed)
    webOut.write(tail)

def processDiff(diffText, mod):

    keywords=[
        ("(module ","Modules",("Component","Reference","Timestamp")),
        ("(gr_text ","Text",("Text","Position")),
        ("(via ","Vias",("Coordinate","Size","Drill","Layers","Net")),
        ("(fp_text ","FP Text",("Reference","Coordinate")),
        ("(pad ","Pads",("Number","Type","Shape","Coordinate","Size","Layers","Ratio")),
        ("(gr_line ","Graphics",("Start","End ","Width","Net")),
        ("(fp_arc","Arcs",("Start","End ","Angle","Width")),
        ("(segment","Segments",("Start","End ","Width","Net","Timestamp")),
        ("(fp_circle","Circles",("Centre","End ","Width")),
    ]

    d={
        "\(start ":"<td>",
        "\(end ":"<td>",
        "\(width ":"<td>",
        "\(tedit ":"<td>",
        "\(tstamp ":"<td>",
        "\(at ":"<td>",
        "\(size ":"<td>",
        "\(drill ":"<td>",
        "\(layers ":"<td>",
        "\(net ":"<td>",
        "\(roundrect_rratio ":"<td>",
        "\(angle ":"<td>",
        "\(center ":"<td>",
        "\)":"</td>",
        "user (\w+)":r'<td>\1</td>',
        "reference (\w+)":r'<td>\1</td>',
        "([0-9]) smd":r'<td>\1</td><td>Surface</td>',
        "roundrect":"<td>Rounded</td>",
        "rect":"<td>Rectangle</td>",
        "(\w.+):(\w.+)":r'<td>\1 \2</td>',
        "(?<=\")(.*)(?=\")":r'<td>\1</td>',
        "[\"]":r'',
        "[**]":r'',
        }

    final =""
    content = ""
    output = ""
    combined = ""
    header = ""
    tbL = ""
    tbR = ""
    checked = "checked"


    top1='''<input name='tabbed' id='tabbed{tabn}' type='radio' {checked}><section><h1><label for='tabbed{tabn}'>{label}</label></h1><div>{content}</div></section>'''
    tsl='''<div class='responsive'>
                <div class = 'tbl'>
                    <table style="border-color: #aaaaaa; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">'''
    tsr='''<div class='responsive'>
                <div class = 'tbr'>
                    <table style="border-color: #aaaaaa; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">'''
    clearfix ='''<div class='clearfix'>
                </div>
                <div style='padding:6px;'>
                </div>'''



    for indx,layerInfo in enumerate(keywords):
        combined = tbL = tbR = ""
        for indx2,parameter in enumerate(layerInfo[2]):
            tbR = tbR + "<th>" + parameter + "</th>"
            tbL = tbL + "<th>" + parameter + "</th>"
        for line in diffText.splitlines():
            if ((layerInfo[0] in line) and (mod in line)):
                output = line.replace(layerInfo[0], "")
                output = output.replace("(layer " + mod + ")", "")
                # print(output)
                for item in d.keys():
                    output = re.sub(item, d[item], output)

                if output.count("<td>") == indx2:
                    output += "<td></td>"
                if output == "<td>":
                    output = ""
                output += "</tr>"
                # print(output)

                if output[0]==">":
                    tbL = tbL + "<tr>" + output[1:]
                elif output[0] == "<":
                    tbR = tbR + "<tr>" + output[1:]

        combined = tsl + tbL + "</table></div></div>" + tsr + tbR + "</table></div></div>"
        content = top1.format(tabn=indx,content=combined,label=layerInfo[1],checked=checked)
        checked=""

        final = final + content
    final = "<div class = 'tabbed'>"+ final + "</div>" + clearfix
    return(final)


def popup_showinfo(progress):
    display = 'Processing: ' + progress
    p = Label(gui, Text=display)
    p.pack()

def scmAvailable():
    SCMS = ''
    if (fossilProg != ''):
        SCMS = SCMS + "Fossil \n"
    if (gitProg != ''):
        SCMS = SCMS + "Git \n"
    if (svnProg != ''):
        SCMS = SCMS + "SVN "
    
    return (SCMS)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.realpath(prjctPath + plotDir), **kwargs)

class Select(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        tk.Toplevel.withdraw(self)
        tk.Toplevel.update(self)
        action = messagebox.askokcancel(
            self,
            message="Select a *.kicad_pcb file under version control",
            detail="Available: \n\n" + SCMS)
        self.update()
        if action == "cancel":
            self.quit()


def startWebServer(port):
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print("serving at port", port)
        webbrowser.open('http://127.0.0.1:' + str(port) + '/web/index.html')
        httpd.serve_forever()


def parse_cli_args():
    parser = argparse.ArgumentParser(description='Kicad PCB visual diffs.')
    parser.add_argument('-d', "--display", type=str, help="Set DISPLAY value, default :1.0", default=':1.0')
    parser.add_argument('-a', "--commit1", type=str, help="Commit1", default='HEAD')
    parser.add_argument('-b', "--commit2", type=str, help="Commit2", default='HEAD')
    parser.add_argument('-s', "--scm", type=str,  help="Select SCM (Git, SVN, Fossil)")
    parser.add_argument('-g', "--gui", action='store_true', help="Use gui")
    parser.add_argument('-p', "--port", type=int, help="Set webserver port", default=9092)
    parser.add_argument('-w', "--webserver-disable", action='store_true', help="Does not execute webserver (just generate images)")
    parser.add_argument("kicad_pcb", help="Kicad PCB")
    args = parser.parse_args()
    print(args)
    return args


if __name__ == "__main__":

    args = parse_cli_args()

    SCMS = scmAvailable()

    if (SCMS == ""):
        print("You need to have at least one SCM program path identified in lines 32 - 40")
        exit()

    prjctPath = os.path.dirname(os.path.realpath(args.kicad_pcb))
    prjctName = os.path.basename(os.path.realpath(args.kicad_pcb))

    print("prjctPath", prjctPath)
    print("prjctName", prjctName)

    if args.scm:
        scm = args.scm

    if args.gui:

        gui = tk.Tk(args.display, SCMS)
        gui.withdraw()
        gui.update()

        Select = Select(gui)
        Select.destroy()

        gui.update()
        gui.deiconify()

        scm = getSCM(_escape_string(prjctPath))
        gui.destroy()

    if args.commit1 == "" and args.commit2 == "":

        if scm == 'Git':
            artifacts = gitDiff(_escape_string(prjctPath), prjctName)
        if scm == 'Fossil':
            artifacts = fossilDiff(_escape_string(prjctPath), prjctName)
        if scm == 'SVN':
            artifacts = svnDiff(_escape_string(prjctPath), prjctName)
        if scm == '':
            print("This project is either not under version control or you have not set the path to the approriate SCM program in lines 32-40")
            sys.exit(0)

        d1, d2 = tkUI.runGUI(artifacts, prjctName, prjctPath, scm)

    else:
        artifacts = []

    d1 = args.commit1
    d2 = args.commit2

    print("Commit1", d1)
    print("Commit2", d2)

    if scm == 'Git':
        times = getGitDiff(d1, d2, prjctName, prjctPath)
    if scm == 'Fossil':
        times = getFossilDiff(d1, d2, prjctName, prjctPath)
    if scm == 'SVN':
        a1, *tail = d1.split(' |')
        d1 = a1[1:]
        a2, *tail = d2.split(' |')
        d2 = a2[1:]
        times = getSVNDiff(d1, d2, prjctName, prjctPath)

    svgDir1, svgDir2, boardDims1, boardDims2 = makeSVG(d1, d2, prjctName, prjctPath)

    makeSupportFiles(prjctName, prjctPath)

    makeOutput(svgDir1, svgDir2, prjctName, prjctPath, times, boardDims1, boardDims2)

    if not args.webserver_disable:
        startWebServer(args.port)
        webbrowser.open('http://127.0.0.1:' + str(args.port) + '/web/index.html')
