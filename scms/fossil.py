
import os
import sys

import subprocess
from subprocess import PIPE, STDOUT, Popen

import settings


def getFossilDiff(diff1, diff2, prjctName, prjctPath):
    '''Given two Fossil artifacts, write out two kicad_pcb files to their respective
    directories (named after the artifacts). Returns the date and time of both commits'''

    artifact1 = diff1[:6]
    artifact2 = diff2[:6]

    findDiff = 'cd ' + _escape_string(prjctPath) + ' && fossil diff --brief -r ' + \
        artifact1 + ' --to ' + artifact2 + ' | ' + settings.grepProg + ' .kicad_pcb'

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
        print("\nThere is no difference in .kicad_pcb file in selected commits")
        sys.exit()

    outputDir1 = prjctPath + settings.plotDir + '/' + artifact1
    outputDir2 = prjctPath + settings.plotDir + '/' + artifact2

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

    return dateTime


def get_fossil_artefacts(path, kicadPCB):
    '''Returns list of Fossil artifacts from a directory containing a
    *.kiartefacts file.'''

    # NOTE Assemble a get_svn_artefacts of artefacts. Unfortunatly, Fossil doesn't give any easily configurable length.
    # NOTE Using the -W option results in multiline diffs
    # NOTE 'fossil -finfo' looks like this
    # 2017-05-19 [21d331ea6b] Preliminary work on CvPCB association and component values (user: johnpateman, artifact: [1100d6e077], branch: Ver_3V3)
    # 2017-05-07 [2d1e20f431] Initial commit (user: johnpateman, artifact: [24336219cc], branch: trunk)
    # NOTE 'fossil -finfo -b' looks like this
    # 21d331ea6b 2017-05-19 johnpate Ver_3V3 Preliminary work on CvPCB association a
    # 2d1e20f431 2017-05-07 johnpate trunk Initial commit
    # TODO Consider parsing the output of fossil finfo and split off date, artifactID, mesage, user and branch

    fossilCmd = 'cd ' + path + ' && ' + settings.fossilProg + ' finfo -b ' + kicadPCB

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

    a, *tail = fArtifacts.split(' |')
    d = a[1:]

    return d
