#!/usr/local/bin/python3

# TODO Add progress tk pages
# TODO Make composite images
# TODO Honour layer selection

# The Python install in macOS is driving me completely mad as you can only run pcbnew
# scripting from a specific version of python2 placed within the Kicad executable. This makes it
# impossible to import pcbnew from another python script especially as I have
# chosen to write the main script in python3. This has annoying consequences as I have to call
# several processes using subprocess calls and saving and then re-reading
# the output rather than simply returning them.

import os
import time
import subprocess
import tkinter as tk
import webbrowser
from subprocess import PIPE, STDOUT, Popen
from tkinter import *
from tkinter import filedialog, ttk
from tkinter.messagebox import showinfo

# import imageme
import PIL
from PIL import Image

import tkUI
from tkUI import *

# TODO Incorporate these full paths

gitProg = '/usr/bin/git'
fossilProg = '/usr/local/bin/fossil'
svnProg = '/usr/bin/svn'
plotDir = '/Plots'
webDir = '/web'
convertProg = '/usr/local/bin/convert'

# pcbDraw = '~/Kicad/PcbDraw/pcbdraw.py'

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


def getGitDiff(diff1, diff2, prjctName, prjctPath):
    '''Given two git artifacts, write out two kicad_pcb files to their respective
    directories (named after the artifact). Returns the date and time of both commits'''

    artifact1 = diff1[:6]
    artifact2 = diff2[:6]

    findDiff = 'cd ' + prjctPath + ' && ' + gitProg + ' diff --name-only ' + \
        artifact1 + ' ' + artifact2 + ' | /usr/bin/grep .kicad_pcb'

    changes = Popen(
        findDiff,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = changes.communicate()

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

    gitArtifact1 = 'cd ' + prjctPath + ' && ' + gitProg + ' show ' + artifact1 + \
        ':' + prjctName + ' > ' + outputDir1 + '/' + prjctName

    gitArtifact2 = 'cd ' + prjctPath + ' && ' + gitProg + ' show ' + artifact2 + \
        ':' + prjctName + ' > ' + outputDir2 + '/' + prjctName

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

    gitDateTime1 = 'cd ' + prjctPath + ' && ' + gitProg + ' show -s --format="%ci" ' + artifact1
    gitDateTime2 = 'cd ' + prjctPath + ' && ' + gitProg + ' show -s --format="%ci" ' + artifact2

    dt1 = Popen(
        gitDateTime1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = dt1.communicate()

    dateTime1 = stdout.decode('utf-8')
    date1, time1, UTC = dateTime1.split(' ')
    print(date1, time1)

    dt2 = Popen(
        gitDateTime2,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = dt2.communicate()

    dateTime2 = stdout.decode('utf-8')
    date2, time2, UTC = dateTime2.split(' ')
    print(date2, time2)

    times = date1 + " " + time1 + " " + date2 + " " + time2

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

    findDiff = 'cd ' + prjctPath + ' && fossil diff --brief -r ' + \
        artifact1 + ' --to ' + artifact2 + ' | grep .kicad_pcb'

    changes = Popen(
        findDiff,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = changes.communicate()

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

    fossilArtifact1 = 'cd ' + prjctPath + ' && fossil cat ' + prjctPath + '/' + prjctName + \
        ' -r ' + artifact1 + ' > ' + outputDir1 + '/' + prjctName
    fossilArtifact2 = 'cd ' + prjctPath + ' && fossil cat ' + prjctPath + '/' + prjctName + \
        ' -r ' + artifact2 + ' > ' + outputDir2 + '/' + prjctName

    fossilInfo1 = 'cd ' + prjctPath + ' && fossil info ' + artifact1
    fossilInfo2 = 'cd ' + prjctPath + ' && fossil info ' + artifact2

    ver1 = Popen(
        fossilArtifact1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = ver1.communicate()

    info1 = Popen(
        fossilInfo1,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = info1.communicate()

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

    info2 = Popen(
        fossilInfo2,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = info2.communicate()

    dateTime = stdout.decode('utf-8')
    dateTime = dateTime.strip()
    uuid, _, _, _, _, _, _, _, _, artifactRef, dateDiff2, timeDiff2, *junk1 = dateTime.split(
        " ")

    dateTime = dateDiff1 + " " + timeDiff1 + " " + dateDiff2 + " " + timeDiff2

    return dateTime


def getProject():

    selected = tk.filedialog.askopenfile(
        initialdir="~/",
        title="Select kicad_pcb file in a VC directory",
        filetypes=(("KiCad pcb files", "*.kicad_pcb"), ("all files", "*.*")))
    if selected:
        path, prjct = os.path.split(selected.name)

    return (path, prjct)


def getSCM(prjctPath):
    '''Determines which SCM methodology is in place when passed the enclosing
    directory. NB no facility to deal with directories with multiple VCS in place.
    Easy to add additional SCMs but also would need to write handling code'''

    scm = ''

    # Check if git
    gitCmd = 'cd ' + prjctPath + ' && ' + gitProg + ' status'
    git = Popen(
        gitCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = git.communicate()
    if ((stdout.decode('utf-8') != '') & (stderr.decode('utf-8') == '')):
        scm = 'Git'

    # check if Fossil
    fossilCmd = 'cd ' + prjctPath + ' && ' + fossilProg + ' status'
    fossil = Popen(
        fossilCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = fossil.communicate()
    if ((stdout.decode('utf-8') != '') & (stderr.decode('utf-8') == '')):
        scm = 'Fossil'

    # check if SVN
    svnCmd = 'cd ' + prjctPath + ' && ' + svnProg + ' log | perl -l40pe "s/^-+/\n/"'
    svn = Popen(
        svnCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = svn.communicate()
    if ((stdout.decode('utf-8') != '') & (stderr.decode('utf-8') == '')):
        scm = 'SVN'

    return scm


def fossilDiff(path, kicadPCB):
    '''Returns list of Fossil artifacts from a directory containing a
    *.kicad_pcb file.'''

    fossilCmd = 'cd ' + path + ' && ' + fossilProg + ' finfo -b ' + kicadPCB
    fossil = Popen(
        fossilCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, _ = fossil.communicate()
    line = (stdout.decode('utf-8').splitlines())
    fArtifacts = [a.replace(' ', '\t\t', 5) for a in line]
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
    gArtifacts = (stdout.decode('utf-8').splitlines())
    return gArtifacts


def svnDiff(path, kicadPCB):
    '''Returns list of SVN resvisions from a directory containing a
    *.kicad_pcb file.'''
    svnCmd = 'cd ' + path + ' && ' + svnProg + ' log -r HEAD:0 | perl -l40pe "s/^-+/\n/"'
    print(svnCmd)
    svn = Popen(
        svnCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = svn.communicate()
    sArtifacts = (stdout.decode('utf-8').splitlines())
    sArtifacts = list(filter(None, sArtifacts))
    return sArtifacts


def makeSVG(d1, d2, prjctName, prjctPath, reqLayers):
    '''Hands off required .kicad_pcb files to "plotPCB2.py"
    and generate .svg files. Does not use the 'reqLayers as the plotting routine
    is written in python2 and can't seem to pass layer list easily. Routine is
    v quick so no major overhead in plotting unescessay layers to svg. Easiest to
    write it to a 'layers' file in the output directory'''

    print("Generating .svg files")

    d1 = d1[:6]
    d2 = d2[:6]

    Diff1 = prjctPath + plotDir + '/' + d1 + '/' + prjctName
    Diff2 = prjctPath + plotDir + '/' + d2 + '/' + prjctName

    d1SVG = '/tmp/svg/' + d1
    d2SVG = '/tmp/svg/' + d2

    if not os.path.exists(d1SVG):
        os.makedirs(d1SVG)
    if not os.path.exists(d2SVG):
        os.makedirs(d2SVG)


#    plot1Cmd = '/usr/local/bin/plotPCB2_DIMS.py ' + Diff1 + " " + d1SVG
#    plot2Cmd = '/usr/local/bin/plotPCB2_DIMS.py ' + Diff2 + " " + d2SVG
#    These should return the board dimensions which might be useful for plotting/alignment

    plot1Cmd = '/usr/local/bin/plotPCB2.py ' + Diff1 + " " + d1SVG
    plot2Cmd = '/usr/local/bin/plotPCB2.py ' + Diff2 + " " + d2SVG

    Popen(
        plot1Cmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    Popen(
        plot2Cmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)

    # if pcbDraw:
    #     prjct, ext = prjctName.split('.')
    #     comp1 = pcbDraw + ' /dev/null ' + d1SVG + '/' + prjct + '-Comp.svg ' + Diff1
    #     comp2 = pcbDraw + ' /dev/null ' + d2SVG + '/' + prjct + '-Comp.svg ' + Diff2
    #     print(comp1, comp2)
    #     Popen(comp1, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    #     Popen(comp2, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)

    return (d1, d2)


def makePNG(svgDir1, svgDir2, qual, prjctName, prjctPath):
    '''Convert svg files in tmp directories in to .png files with defined
    quality (dpi)'''

    svgDirTop = '/tmp/svg/' + svgDir1 + '/'
    svgDirBottom = '/tmp/svg/' + svgDir2 + '/'
    qual = str(qual.get())

    svgdirs = []

    svgdirs.append(svgDirTop)
    svgdirs.append(svgDirBottom)

    for d in svgdirs:
        directory = os.fsencode(d)

        _, _, _, diff, e = d.split('/')
        print("Converting .svg files in ", d, e, " to .png")

        pngFullPath = prjctPath + plotDir + '/' + diff

        if not os.path.exists(pngFullPath):
            os.makedirs(pngFullPath)

        for file in os.listdir(directory):

            filename = os.fsdecode(file)

            if filename.endswith(".svg"):
                basename, ext = filename.split('.')
                command1 = convertProg + ' -density ' + qual + ' -fuzz 10% -trim +repage ' + \
                    d + filename + ' ' + d + basename + '.png'

                svgs = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE)
                out, err = svgs.communicate()

        print("Inverting .png files in ", d, e)
        for file in os.listdir(directory):

            filename = os.fsdecode(file)

            if filename.endswith(".png"):

                basename, ext = filename.split('.')

                """
                The -negate option replaces each pixel with its complementary color. The -channel RGB 
                option is necessary as of ImageMagick 7 to prevent the alpha channel (if present) 
                from being negated. 
                """
                command2 = convertProg + ' ' + d + basename + '.png -channel RGB -negate ' + \
                    prjctPath + plotDir + '/' + diff + '/' + basename + '.png'

                pngs = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE)
                out, err = pngs.communicate()


def comparePNG(diff1, diff2, prjctName, prjctPath):
    '''Generate png diffs between DIFF_1 and DIFF_2. Originally the intention was
    to use the ImageMagic 'composite stereo 0' function to identify
    where items have moved but I could not get this to work.
    This flattens the original files to greyscale and they need to be converted
    back to rgb in order to be colourised.'''

    diffDir = prjctPath + plotDir + '/diff-' + diff1 + '-' + diff2

    print("Generating *.png diff files")
    if not os.path.exists(diffDir):
        os.makedirs(diffDir)

    pngFullPath1 = prjctPath + plotDir + '/' + diff1
    pngFullPath2 = prjctPath + plotDir + '/' + diff2

    pngBasePath = prjctPath + plotDir

    directory1 = os.fsencode(pngFullPath1)

    for file in os.listdir(directory1):
        plot = os.fsdecode(file)
        if plot.endswith(".png"):
            p1 = pngBasePath + '/' + diff1 + '/' + plot
            p2 = pngBasePath + '/' + diff2 + '/' + plot
            c1 = convertProg + ' ' + p1 + ' -flatten -grayscale Rec709Luminance ' + p1
            c2 = convertProg + ' ' + p2 + ' -flatten -grayscale Rec709Luminance ' + p2
            composite = convertProg + ' ' + p1 + ' ' + p2 + \
                ' "(" -clone 0-1 -compose darken -composite ")" -channel RGB -combine ' + \
                diffDir + '/' + plot
            
            comp1 = subprocess.Popen(c1, shell=True, executable='/bin/bash')
            comp2 = subprocess.Popen(c2, shell=True, executable='/bin/bash')

            diffs = subprocess.Popen(composite, shell=True, executable='/bin/bash')
            out, err = diffs.communicate()
            
            # Accounts for project names containing hyphens
            splitted = plot.split('-')
            page = splitted[-2]
            layerExt = splitted[-1]
            
            layer, ext = layerExt.split('.')

            colour = layerCols.get(layer, '#ffffff')
            print(layer, colour)

            colourize = convertProg + ' ' + diffDir + '/' + plot + ' -fill "' + colour + \
                '" -fuzz 75% -opaque "#ffffff" ' + diffDir + '/' + plot
            
            diffs = subprocess.Popen(colourize, shell=True, stdout=subprocess.PIPE)
            out, err = diffs.communicate()

            col1A = convertProg + ' ' + p1 + ' -define png:color-type=2 ' + p1
            col1 = convertProg + ' ' + p1 + ' -fill "' + colour + '" -fuzz 75% -opaque "#ffffff" ' + p1

            col2A = convertProg + ' ' + p2 + ' -define png:color-type=2 ' + p2
            col2 = convertProg + ' ' + p2 + ' -fill "' + colour + '" -fuzz 75% -opaque "#ffffff" ' + p2

            colour1 = subprocess.Popen(col1A, shell=True, stdout=subprocess.PIPE)
            out, err = colour1.communicate()

            colour1 = subprocess.Popen(col1, shell=True, stdout=subprocess.PIPE)
            out, err = colour1.communicate()

            colour2 = subprocess.Popen(col2A, shell=True, stdout=subprocess.PIPE)
            out, err = colour2.communicate()

            colour2 = subprocess.Popen(col2, shell=True, stdout=subprocess.PIPE)
            out, err = colour2.communicate()


def makeSupportFiles(prjctName, prjctPath):
    '''Setup web directories for output
    '''

    webd = prjctPath + plotDir + webDir
    webIndex = webd + '/index.html'

    if not os.path.exists(webd):
        os.makedirs(webd)
        os.makedirs(webd + '/thumbs')
        os.makedirs(webd + '/tryptych')

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
                        prms[key] = words[1].strip("\t ()")
    return(prms)


def makeOutput(diffDir1, diffDir2, prjctName, prjctPath, times):
    '''Write out HTML using template. Iterate through files in diff directories, generating
    thumbnails and three way view (tryptych) page.
    '''
    webd = prjctPath + plotDir + webDir

    board1 = prjctPath + "/" + plotDir + "/" + diffDir1 + "/" + prjctName
    board2 = prjctPath + "/" + plotDir + "/" + diffDir2 + "/" + prjctName

    webIndex = webd + '/index.html'

    webOut = open(webIndex, 'w')

    D1DATE, D1TIME, D2DATE, D2TIME = times.split(" ")

    board_1_Info = getBoardData(board1)
    board_2_Info = getBoardData(board2)

    print(board_1_Info)
    print(board_2_Info)

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

    # TODO Improve CSS colourscheme

    indexHead = '''
    <!DOCTYPE HTML>
    <html lang="en">
    <head>
    <link rel="stylesheet" type="text/css" href="style.css" media="screen" />

    </head>

    <table style="border-color: #aaaaaa; width: 100%; height: 2px;" border="2px" cellspacing="2px" cellpadding="3px">
    <tbody>
    <tr>
    <td colspan="6" width="256">
    <h1>{TITLE}
    <h5>{DATE}
    <h5>{COMPANY}
    </td>
    </tr>
    <tr>
    <td width="83">
    <div class = "h3"><b>Version</b></div>
    </td>
    <td width="89">
    <div class="h2 green">{diffDir1}</div>
    </td>
    <td width="89">
    <div class="h2 red">{diffDir2}</div>
    </td>
    <td width="84">
    <div class="h3">Thickness (mm)</div>
    </td>
    <td width="40">
    <div class="h2 green">{THICK1}</div>
    </td>
    <td width="41">
    <div class="h2 red">{THICK2}</div>
    </td>
    </tr>
    <tr>
    <td width="83">
    <div class="h2">Date</div>
    </td>
    <td width="89">
    <div class="h3">{D1DATE}</div>
    </td>
    <td width="89">
    <div class="h3">{D2DATE}</div>
    </td>
    <td width="84">
    <div class="h3">Drawings</div>
    </td>
    <td width="40">
    <div class="h2 green">{DRAWINGS1}</div>
    </td>
    <td width="41">
    <div class="h2 red">{DRAWINGS2}</div>
    </td>
    </tr>
    <tr>
    <td width="83">
    <div class="h3"><strong>Time</div>
    </td>
    <td width="89">
    <div class="h3">{D1TIME}</div>
    </td>
    <td width="89">
    <div class="h3">{D2TIME}</div>
    </td>
    <td width="84">
    <div class="h3">Tracks</div>
    </td>
    <td width="40">
    <div class="h2 green">{TRACKS1}</div>
    </td>
    <td width="41">
    <div class="h2 red">{TRACKS2}</div>
    </td>
    </tr>
    <tr>
    <td colspan="3" rowspan="3" width="261">
    </td>
    <td width="84">
    <div class="h3">Zones</div>
    </td>
    <td width="40">
    <div class="h2 green">{ZONES1}</div>
    </td>
    <td width="41">
    <div class="h2 red">{ZONES2}</div>
    </td>
    </tr>
    <tr>
    <td width="84">
    <div class="h3">Modules</div>
    </td>
    <td width="40">
    <div class="h2 green">{MODULES1}</div>
    </td>
    <td width="41">
    <div class="h2 red">{MODULES2}</div>
    </td>
    </tr>
    <tr>
    <td width="84">
    <div class="h3">Nets</div>
    </td>
    <td width="40">
    <div class="h2 green">{NETS1}</div>
    </td>
    <td width="41">
    <div class="h2 red">{NETS2}</div>
    </td>
    </tr>
    </tbody>
    </table>
    '''.format(
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
        NETS2=NETS2)

    webOut.write(indexHead)

    diffCmnd1 = ()

    source = prjctPath + plotDir + '/diff-' + diffDir1 + '-' + diffDir2 + '/'

    thumbDir = prjctPath + plotDir + webDir + '/thumbs'

    if not os.path.exists(thumbDir):
        os.makedirs(thumbDir)

    tryptychDir = prjctPath + plotDir + webDir + '/tryptych'

    if not os.path.exists(tryptychDir):
        os.makedirs(tryptychDir)

    diffs = os.fsencode(source)
    size = 300, 245
    for f in os.listdir(diffs):
        filename = os.fsdecode(f)
        if filename.endswith(".png"):
            outfile = thumbDir + '/th_' + filename
            tryptych = tryptychDir + '/' + filename + '.html'
            *project, layer = filename.split('-')
            im = PIL.Image.open(source + filename)
            im.thumbnail(size, PIL.Image.ANTIALIAS)
            im.save(outfile, "png")

            outfile = '''
<div class="responsive">
  <div class="gallery">
    <a target="_blank" href = tryptych/{0}.html>
      <img src = thumbs/th_{0} height="200">
    </a>
    <div class="desc">{1}</div>
  </div>
</div>
            '''.format(filename, layer[:-4])
            webOut.write(outfile)

            tryptychOut = open(tryptych, 'w')

            tryptychHTML = '''
<!DOCTYPE HTML>
<html lang="en">
<head>
<link rel="stylesheet" type="text/css" href="../style.css" media="screen" />
<style>
div.responsive {{
   padding: 0 6px;
   float: left;
   width: 49.99%;
   }}
</style>
</head>

<body>
<h2>{layername}</h> <br>

<div class="responsive" >
    <div class="gallery" >
        <a target="_blank" href={layername}.html>
            <a href=../../{diff1}/{layername}> <img src=../../{diff1}/{layername} width="500"> </a>
        </a>
        <div class="desc green">{diff1}</div>
    </div>
</div>

<div class="responsive" >
    <div class="gallery" >
        <a target="_blank" href = {layername}.html>
            <a href=../../{diff2}/{layername} > <img src = ../../{diff2}/{layername} width = "500" > </a>
        </a>
        <div class="desc red" >{diff2}</div>
    </div>
</div>

<div class="responsive" >
    <div class="gallery" >
        <a target="_blank" href = ./{plotDir}/{layername}.html>
            <a href= ../../diff-{diff1}-{diff2}/{layername}> <img src = ../../diff-{diff1}-{diff2}/{layername} width = "500" > </a>
        </a>
        <div class="desc white" > Composite </div>
    </div>
</div>'''.format(
                layername=filename,
                diff1=diffDir1,
                diff2=diffDir2,
                plotDir=plotDir)

            tryptychOut.write(tryptychHTML)

            prjct, ext = filename.split('.')

            # Accounts for project names containing hyphens
            splitted = prjct.split('-')
            prj = splitted[-2]
            layer = splitted[-1]

            #prj, layer = prjct.split('-')
            print(prj, layer)
            layer = layer.replace('_', '.')

            if not diffCmnd1:
                diffCmnd1 = 'diff {prjctPath}{plotDir}/{diff2}/*.kicad_pcb {prjctPath}{plotDir}/{diff1}/*.kicad_pcb >> {prjctPath}{plotDir}/diff-{diff1}-{diff2}/diff.txt'.format(
                    plotDir=plotDir,
                    diff1=diffDir1,
                    diff2=diffDir2,
                    prjctPath=prjctPath)
                print(diffCmnd1)

                diffCmnd2 = '''diff {prjctPath}{plotDir}/{diff2}/*.kicad_pcb {prjctPath}{plotDir}/{diff1}/*.kicad_pcb | grep {mod} | sed 's/>  /<\/div><div class="differences added">/g' | sed 's/<   /<\/div><div class="differences removed">/g' | sed 's/\/n/<\/div>/g' '''.format(
                    layername=filename,
                    plotDir=plotDir,
                    diff1=diffDir1,
                    diff2=diffDir2,
                    prjctPath=prjctPath,
                    mod=layer,
                    webDir=webDir)

                diff1Txt = Popen(
                    diffCmnd1,
                    shell=True,
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    close_fds=True)
                stdout, stderr = diff1Txt.communicate()

                diff2Txt = Popen(
                    diffCmnd2,
                    shell=True,
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=PIPE,
                    close_fds=True)
                stdout, stderr = diff2Txt.communicate()
                out = stdout.decode('utf8')

            tryptychOut.write(out)

            tail = '''
<div class="clearfix"></div>
<div style="padding:6px;">
</div>'''
            tryptychOut.write(tail)

    tail = '''
<div class="clearfix"></div>
<div style="padding:6px;">
</div>'''

    webOut.write(tail)


def popup_showinfo(progress):
    display = 'Processing: ' + progress
    p = Label(gui, Text=display)
    p.pack()


class Splash(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        tk.Toplevel.withdraw(self)
        tk.Toplevel.update(self)
        action = messagebox.askokcancel(
            self,
            message="Select a *.kicad_pcb file under version control",
            detail="Git, Fossil or SVN supported")
        self.update()
        if action == "cancel":
            self.quit()


# class Progress(tk.Toplevel):
#     def __init__(self, parent):
#         tk.Toplevel.__init__(self, parent)
#         tk.Toplevel.withdraw(self)
#         tk.Toplevel.update(self)
#         action = label(
#             self,
#             message=progress).pack()
#         self.update()


if __name__ == "__main__":

    gui = tk.Tk()
    gui.withdraw()
    gui.update()
    splash = Splash(gui)
    splash.destroy()
    prjctPath, prjctName = getProject()
    gui.update()
    gui.deiconify()

    scm = getSCM(prjctPath)

    print(scm)

    gui.destroy()

    if scm == 'Git':
        artifacts = gitDiff(prjctPath, prjctName)
    if scm == 'Fossil':
        artifacts = fossilDiff(prjctPath, prjctName)
    if scm == 'SVN':
        artifacts = svnDiff(prjctPath, prjctName)

    dpi, d1, d2, layers = tkUI.runGUI(artifacts, prjctName, prjctPath, scm)

    print("Resolution (dpi) : ", dpi.get())
    print("Commit1", d1)
    print("Commit2", d2)

    selectedLayers = []

    if not os.path.exists('/tmp/svg'):
        os.makedirs('/tmp/svg')

    # progress = StringVar()
    # progress.set('Processing')
    # m = Label(gui, textvariable=progress)
    # m.pack()
    with open('/tmp/svg/layers', 'w') as f:
        for l in layers:
            # progress.set("Layer: " + l)
            # gui.update_idletasks()
            if layers[l].get() == 1:
                f.write(l)
                f.write('\n')

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

    svgDir1, svgDir2 = makeSVG(d1, d2, prjctName, prjctPath, selectedLayers)

    # Sometimes the SVG just created did not register with the system
    # resulting in makePNG believing there was no SVG present
    time.sleep(1)

    makePNG(svgDir1, svgDir2, dpi, prjctName, prjctPath)

    # outpng = pcbdraw.draw_pretty_pcb(prjctName)

    comparePNG(svgDir1, svgDir2, prjctName, prjctPath)

    makeSupportFiles(prjctName, prjctPath)

    # imageme.serve_dir(prjctPath + plotDir)

    makeOutput(svgDir1, svgDir2, prjctName, prjctPath, times)

    webbrowser.open(
        'file://' + os.path.realpath(prjctPath + plotDir + webDir + '/index.html'))
