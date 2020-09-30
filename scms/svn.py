
import os
import sys

import subprocess
from subprocess import PIPE, STDOUT, Popen

import settings


def get_boards(diff1, diff2, prjctName, prjctPath):
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
        print("\nThere is no difference in .kicad_pcb file in selected commits")
        sys.exit()

    outputDir1 = prjctPath + settings.plotDir + '/' + diff1
    outputDir2 = prjctPath + settings.plotDir + '/' + diff2

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

    return (times)


def get_artefacts(path, kicadPCB):
    '''Returns list of SVN resvisions from a directory containing a
    *.kicad_pcb file.'''

    svnCmd = 'cd ' + path + ' && ' + settings.svnProg + ' log -r HEAD:0 | perl -l40pe "s/^-+/\n/"'

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


def get_kicad_project_path(prjctPath):
    return "./"