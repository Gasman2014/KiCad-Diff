#!/usr/bin/env python3
#
# A python script to select two revisions of a KiCad pcbnew layout
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

import sys
import os
import tempfile
import tkinter as tk
import webbrowser
from subprocess import PIPE, STDOUT, Popen
from tkinter import *
from tkinter import filedialog, ttk
from tkinter.messagebox import showinfo
import tkUI
from tkUI import *
import http.server
import argparse
from kidiff_html import *

if sys.version_info[0] >= 3:
    unicode = str


def _escape_string(val):
    # Make unicode
    val = unicode(val)
    # Escape stuff
    val = val.replace(u'\\', u'\\\\')
    val = val.replace(u' ', u'\\ ')
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
executablePath = os.path.dirname(os.path.realpath(__file__))
plotProg = os.path.join(executablePath, 'plotPCB.py')
plotDir = 'plots'
webDir = 'web'

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

# ----------------------Main Functions begin here---------------------------------------
#

def getGitPath(prjctName, prjctPath):
    gitRootCmd = f"cd {prjctPath} && {gitProg} rev-parse --show-toplevel"
    gitRootProcess = Popen(
        gitRootCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = gitRootProcess.communicate()
    gitRoot = stdout.decode('utf-8')

    gitPathCmd = f"cd {_escape_string(gitRoot)} && {gitProg} ls-tree -r --name-only HEAD | {grepProg} -m 1 {_escape_string(prjctName)}"
    print(gitPathCmd)
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


def getGitDiff(diff1, diff2, prjctName, prjctPath, outputPath=None):
    '''Given two git artifacts, write out two kicad_pcb files to their respective
    directories (named after the artifact). Returns the date and time of both commits'''

    if outputPath is None:
        outputPath = prjctPath

    artifact = [diff1[:6], diff2[:6]]

    findDiff = f"cd {_escape_string(prjctPath)} && {gitProg} diff --name-only " + \
        f"{artifact[0]} {artifact[1]} . | {grepProg} .kicad_pcb"

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

    outputDir = [os.path.join(outputPath, plotDir, art) for art in artifact]

    for outd in outputDir:
        if not os.path.exists(outd):
            os.makedirs(outd)

    gitPath = getGitPath(prjctName, _escape_string(prjctPath))

    gitArtifact = [f"cd {_escape_string(prjctPath)} && {gitProg} show {art}:{gitPath} > {os.path.join(_escape_string(outd), _escape_string(prjctName))}" for art, outd in zip(artifact, outputDir)]

    print(gitArtifact)

    ver = [Popen(
        gart,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True) for gart in gitArtifact]

    for v in ver:
        stdout, stderr = v.communicate()
        v.wait()

    gitDateTime = [f"cd {_escape_string(prjctPath)} && {gitProg} show -s --format=\"%ci\" {art}" for art in artifact]

    print(gitDateTime)

    dt = [Popen(
        gdt,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True) for gdt in gitDateTime]

    dateTime = []
    for d in dt:
        stdout, stderr = d.communicate()
        d.wait()
        dateTime.append(stdout.decode('utf-8'))

    dtu = [(dt.split(' ')) for dt in dateTime]

    times = f"{dtu[0][0]} {dtu[0][1]} {dtu[1][0]} {dtu[1][1]}"
    print(times)
    return (times)


def getSVNDiff(diff1, diff2, prjctName, prjctPath, outputPath=None):
    '''Given two SVN revisions, write out two kicad_pcb files to their respective
    directories (named after the revision number). Returns the date and time of both commits'''

    if outputPath is None:
        outputPath = prjctPath

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

    outputDir1 = outputPath + plotDir + '/' + diff1
    outputDir2 = outputPath + plotDir + '/' + diff2

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


def getFossilDiff(diff1, diff2, prjctName, prjctPath, outputPath=None):
    '''Given two Fossil artifacts, write out two kicad_pcb files to their respective
    directories (named after the artifacts). Returns the date and time of both commits'''

    if outputPath is None:
        outputPath = prjctPath

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

    outputDir1 = outputPath + plotDir + '/' + artifact1
    outputDir2 = outputPath + plotDir + '/' + artifact2

    if not os.path.exists(outputDir1):
        os.makedirs(outputDir1)

    if not os.path.exists(outputDir2):
        os.makedirs(outputDir2)

    fossilArtifact1 = 'cd ' + _escape_string(prjctPath) + ' && fossil cat ' + _escape_string(prjctPath) + '/' + _escape_string(prjctName) + \
        ' -r ' + artifact1 + ' > ' + outputDir1 + '/' + _escape_string(prjctName)
    fossilArtifact2 = 'cd ' + _escape_string(prjctPath) + ' && fossil cat ' + _escape_string(prjctPath) + '/' + _escape_string(prjctName) + \
        ' -r ' + artifact2 + ' > ' + outputDir2 + '/' + _escape_string(prjctName)

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


def getProject(display, scms):
    '''File select dialogue. Opens Tk File browser and
    selector set for .kicad_pcb files. Returns path and file name
    '''
    gui = tk.Tk(display, scms)
    gui.withdraw()
    gui.update()
    select = Select(gui)
    select.destroy()

    selected = tk.filedialog.askopenfile(
        initialdir="~/",
        title="Select kicad_pcb file in a VC directory",
        filetypes=(("KiCad pcb files", "*.kicad_pcb"), ("all files", "*.*")))
    if selected:
        path, prjct = os.path.split(selected.name)

    gui.destroy()
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
    artifacts = [a.replace(' ', '\t', 4) for a in line]
    return artifacts


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
    artifacts = (stdout.decode('utf-8').splitlines())
    return artifacts


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
    artifacts = (stdout.decode('utf-8').splitlines())
    artifacts = list(filter(None, artifacts))
    return artifacts


def makeSVG(d1, d2, prjctName, prjctPath, outputPath=None):
    '''Hands off required .kicad_pcb files to "plotPCB.py"
    and generate SVG files.

    Routine is very quick so all layers are plotted to SVG.'''

    print("Generating .svg files")

    commitDir = [d1[:6], d2[:6]]

    if outputPath is None:
        outputPath = prjctPath

    diffDir = [os.path.join(outputPath, plotDir, cmtDir, prjctName) for cmtDir in commitDir]

    svgDir = [os.path.join(outputPath, plotDir, cmtDir) for cmtDir in commitDir]
    for d in svgDir:
        if not os.path.exists(d):
            os.makedirs(d)

    plotCmd = [f"{_escape_string(plotProg)} {_escape_string(dff)} {_escape_string(dsvg)}" for dff, dsvg in zip(diffDir, svgDir)]

    plot = [
        Popen(
            cmd,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            close_fds=True
        ) for cmd in plotCmd
    ]

    plotDims = []
    for plt, idx in zip(plot, range(len(plot))):
        stdout, stderr = plt.communicate()
        plotDims.append((stdout.decode('utf-8').splitlines()))
        errors = stderr.decode('utf-8')
        if errors != "":
            print(f"Plot{idx} error: {errors}")
        plt.wait()

    return (commitDir[0], commitDir[1], plotDims[0][0], plotDims[1][0])


def makeSupportFiles(prjctName, prjctPath, outputPath=None):
    '''
    Setup web directories for output
    '''

    if outputPath is None:
        outputPath = prjctPath

    webd = os.path.join(outputPath, plotDir, webDir)
    webIndex = os.path.join(webd, 'index.html')
    webStyle = os.path.join(webd, 'style.css')

    if not os.path.exists(webd):
        os.makedirs(webd)
        os.makedirs(os.path.join(webd, 'tryptych'))

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

    with open(board, 'r') as f:
        for line in f:
            words = line.strip("\t ()").split()
            for key in prms:
                if len(words) > 1:
                    if key == words[0]:
                        complete = ""
                        for i in range(1, len(words)):
                            complete += words[i].strip("\t ()").replace("\"", "") + " "
                        prms[key] = complete
    print(prms)
    return(prms)


def makeOutput(diffDir1, diffDir2, prjctName, prjctPath, times, dim1, dim2, outputPath=None):
    '''Write out HTML using template. Iterate through files in diff directories, generating
    thumbnails and three way view (tryptych) page.
    '''

    if outputPath is None:
        outputPath = prjctPath

    webd = os.path.join(outputPath, plotDir, webDir)

    board1 = os.path.join(outputPath, plotDir, diffDir1, prjctName)
    board2 = os.path.join(outputPath, plotDir, diffDir2, prjctName)

    webIndex = os.path.join(webd, 'index.html')

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

    index = indexHead.format(
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

    source = os.path.join(outputPath, plotDir, diffDir1) + '/'

    tryptychDir = os.path.join(outputPath, plotDir, webDir, 'tryptych')
    if not os.path.exists(tryptychDir):
        os.makedirs(tryptychDir)

    # diffs = os.fsencode(source)

    for f in os.listdir(source):
        filename = os.fsdecode(f)
        if filename.endswith(".svg"):
            print(filename)
            file, file_extension = os.path.splitext(filename)
            tryptych = os.path.join(tryptychDir, file + '.html')
            *project, layer = filename.split('-')
            layer, ext = layer.split('.')
            prjct, ext = filename.split('.')
            # Accounts for project names containing hyphens
            splitted = prjct.split('-')
            prj = "-".join(splitted[0:-1])
            layer = splitted[-1]
            out = outfile.format(
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

            diffbase = diffProg + "{prjctPath}/{plotDir}/{diff2}/*.kicad_pcb {prjctPath}/{plotDir}/{diff1}/*.kicad_pcb >> {prjctPath}/{plotDir}/diff.txt"

            if not diffCmnd1:
                diffCmnd1 = diffbase.format(
                    plotDir=plotDir,
                    diff1=diffDir1,
                    diff2=diffDir2,
                    prjctPath=_escape_string(prjctPath))

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
            mod = layer.replace("_", ".")
            #            diffCmnd2 = diffProg + ''' --suppress-common-lines {prjctPath}/{plotDir}/{diff2}/*.kicad_pcb {prjctPath}/{plotDir}/{diff1}/*.kicad_pcb | grep {mod} | sed 's/>  /<\/div><div class="differences added">/g' | sed 's/<   /<\/div><div class="differences removed">/g' | sed 's/\/n/<\/div>/g' | sed 's/(status [1-9][0-9])//g' '''.format(
            diffCmnd2 = diffProg + ''' --suppress-common-lines {prjctPath}/{plotDir}/{diff2}/*.kicad_pcb {prjctPath}/{plotDir}/{diff1}/*.kicad_pcb | {grepProg} {mod} | sed 's/(status [1-9][0-9])//g' '''.format(
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
            processed += twoPane

            tryptychOut.write(processed)
    webOut.write(tail)


def processDiff(diffText, mod):

    keywords = [
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

    d = {
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

    final = ""
    content = ""
    output = ""
    combined = ""
    header = ""
    tbL = ""
    tbR = ""
    checked = "checked"

    top1 = '''<input name='tabbed' id='tabbed{tabn}' type='radio' {checked}><section><h1><label for='tabbed{tabn}'>{label}</label></h1><div>{content}</div></section>'''
    tsl = '''<div class='responsive'>
                <div class = 'tbl'>
                    <table style="border-color: #aaaaaa; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">'''
    tsr = '''<div class='responsive'>
                <div class = 'tbr'>
                    <table style="border-color: #aaaaaa; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">'''
    clearfix = '''<div class='clearfix'>
                </div>
                <div style='padding:6px;'>
                </div>'''

    for indx, layerInfo in enumerate(keywords):
        combined = tbL = tbR = ""
        for indx2, parameter in enumerate(layerInfo[2]):
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
        content = top1.format(tabn=indx, content=combined, label=layerInfo[1], checked=checked)
        checked = ""

        final = final + content
    final = f"<div class = 'tabbed'>{final}</div>{clearfix}"
    return(final)


def popup_showinfo(progress):
    display = 'Processing: ' + progress
    p = Label(gui, Text=display)
    p.pack()


def scmAvailable():
    scms = ''
    if fossilProg != '':
        scms = scms + "Fossil \n"
    if gitProg != '':
        scms = scms + "Git \n"
    if svnProg != '':
        scms = scms + "SVN "
    return (scms)


class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = http.server.SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath


class HTTPServer(http.server.HTTPServer):
    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        http.server.HTTPServer.__init__(self, server_address, RequestHandlerClass)


class Select(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        tk.Toplevel.withdraw(self)
        tk.Toplevel.update(self)
        action = messagebox.askokcancel(
            self,
            message="Select a *.kicad_pcb file under version control",
            detail="Available: \n\n" + scms)
        self.update()
        if action == "cancel":
            self.quit()


def startWebServer(port, assetPath):
    with HTTPServer(assetPath, ("", port)) as httpd:
        print("serving at port", port)
        webbrowser.open('http://127.0.0.1:' + str(port) + '/web/index.html')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

def parse_cli_args():
    parser = argparse.ArgumentParser(description='KiCad PCB visual diffs.')
    parser.add_argument('-a', "--commit1", type=str, help="Commit1")
    parser.add_argument('-b', "--commit2", type=str, help="Commit2")
    parser.add_argument('-d', "--display", type=str, help="Set DISPLAY value, default :1.0", default=':1.0')
    parser.add_argument('-p', "--port", type=int, help="Set webserver port", default=9092)
    parser.add_argument('-s', "--scm", type=str,  help="Select SCM (Git, SVN, Fossil)")
    parser.add_argument('-w', "--webserver-disable", action='store_true', help="Does not execute webserver (just generate images)")
    parser.add_argument("kicad_pcb", nargs='?', help="KiCad PCB")
    args = parser.parse_args()
    print(args)
    return args

if __name__ == "__main__":

    args = parse_cli_args()

    scms = scmAvailable()
    if scms == "":
        print("You need to have at least one SCM program path specified.")
        exit()

    if args.kicad_pcb is None:
        prjctPath, prjctName = getProject(args.display, scms)
    else:
        prjctPath = os.path.dirname(os.path.realpath(args.kicad_pcb))
        prjctName = os.path.basename(os.path.realpath(args.kicad_pcb))

    print(f"prjctPath {prjctPath}")
    print(f"prjctName {prjctName}")

    if args.scm:
        scm = args.scm.lower()
    else:
        scm = getSCM(_escape_string(prjctPath)).lower()

    if scm == 'git':
        scmDiff = gitDiff
    elif scm == 'fossil':
        scmDiff = fossilDiff
    elif scm == 'svn':
        scmDiff = svnDiff
    else:
        print("This project is either not under version control or you have not set the path to the approriate SCM program in lines 32-40")
        sys.exit(0)

    with tempfile.TemporaryDirectory() as tmpDir:
        artifacts = scmDiff(_escape_string(prjctPath), prjctName)

        if args.commit1 is None and args.commit2 is None:
            d1, d2 = tkUI.runGUI(artifacts, prjctName, prjctPath, scm)
        else:
            d1 = args.commit1
            d2 = args.commit2
            if args.commit1 is None:
                d1 = artifacts[0]
            if args.commit2 is None:
                d2 = artifacts[0]

        print(f"Commit1 {d1}")
        print(f"Commit2 {d2}")
        print(f"prjctName {prjctName}")
        print(f"prjctPath {prjctPath}")

        if scm == 'git':
            getDiff = getGitDiff
        elif scm == 'fossil':
            getDiff = getFossilDiff
        elif scm == 'svn':
            a1, *tail = d1.split(' |')
            d1 = a1[1:]
            a2, *tail = d2.split(' |')
            d2 = a2[1:]
            getDiff = getSVNDiff
        times = getDiff(d1, d2, prjctName, prjctPath, outputPath=tmpDir)

        svgDir1, svgDir2, boardDims1, boardDims2 = makeSVG(
            d1, d2,
            prjctName, prjctPath,
            outputPath=tmpDir
            )

        makeSupportFiles(
            prjctName, prjctPath,
            outputPath=tmpDir
            )

        makeOutput(
            svgDir1, svgDir2,
            prjctName, prjctPath,
            times,
            boardDims1, boardDims2,
            outputPath=tmpDir
            )

        if not args.webserver_disable:
            startWebServer(args.port, os.path.realpath(os.path.join(tmpDir, plotDir)))
