
import os
import sys

import subprocess
from subprocess import PIPE, STDOUT, Popen

import settings


def getGitPath(prjctName, prjctPath):

    gitRootCmd = 'cd ' + settings.escape_string(prjctPath) + ' && ' + settings.gitProg + ' rev-parse --show-toplevel'

    gitRootProcess = Popen(
        gitRootCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = gitRootProcess.communicate()

    gitRoot = stdout.decode('utf-8')

    gitPathCmd = 'cd ' + settings.escape_string(gitRoot) + ' && ' + settings.gitProg + ' ls-tree -r --name-only HEAD | ' + settings.grepProg + ' -m 1 ' + prjctName

    gitPathProcess = Popen(
        gitPathCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = gitPathProcess.communicate()

    gitPathProcess.wait()

    return settings.escape_string(stdout.decode('utf-8'))

def get_git_files(diff1, diff2, prjctName, kicad_project_path, prjctPath):
    '''Given two git artifacts, write out two kicad_pcb files to their respective
    directories (named after the artifact). Returns the date and time of both commits'''

    artifact1 = diff1[:6]
    artifact2 = diff2[:6]

    findDiff = \
        'cd ' + settings.escape_string(prjctPath) + ' && ' + \
        settings.gitProg + ' diff --name-only ' + artifact1 + ' ' + artifact2 + ' . | ' + \
        settings.grepProg + " '^" + kicad_project_path + "/" + prjctName + "'"

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

    outputDir1 = prjctPath + '/' + settings.plotDir + '/' + kicad_project_path + '/' + artifact1
    outputDir2 = prjctPath + '/' + settings.plotDir + '/' + kicad_project_path + '/' + artifact2

    if not os.path.exists(outputDir1):
        os.makedirs(outputDir1)

    if not os.path.exists(outputDir2):
        os.makedirs(outputDir2)

    gitPath = getGitPath(settings.escape_string(kicad_project_path) + "/" + prjctName, settings.escape_string(prjctPath))

    gitArtifact1 = 'cd ' + settings.escape_string(prjctPath) + ' && ' + \
        settings.gitProg + ' show ' + artifact1 + ':' + gitPath + ' > ' + \
        settings.escape_string(outputDir1) + '/' + prjctName

    gitArtifact2 = 'cd ' + settings.escape_string(prjctPath) + ' && ' + \
        settings.gitProg + ' show ' + artifact2 + ':' + gitPath + ' > ' + settings.escape_string(outputDir2) + '/' + prjctName

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

    ver1.wait()
    ver2.wait()

    gitDateTime1 = 'cd ' + settings.escape_string(prjctPath) + ' && ' + settings.gitProg + ' show -s --format="%ci" ' + artifact1
    gitDateTime2 = 'cd ' + settings.escape_string(prjctPath) + ' && ' + settings.gitProg + ' show -s --format="%ci" ' + artifact2

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

    time1 = date1 + " " + time1
    time2 = date2 + " " + time2

    return time1 + " " + time2

def get_git_artefacts(path, kicadPCB, kicad_project_path):
    '''Returns list of Git artifacts from a directory containing a
    *.kicad_pcb file.'''

    gitCmd = 'cd ' + path + ' && ' + settings.gitProg + ' log --pretty=format:"%h | %s"'

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

def get_git_kicad_project_path(prjctPath):

    gitRootCmd = 'cd ' + settings.escape_string(prjctPath) + ' && ' + settings.gitProg + ' rev-parse --show-toplevel'
    gitRootProcess = Popen(
        gitRootCmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)
    stdout, stderr = gitRootProcess.communicate()
    gitRoot = stdout.decode('utf-8').strip()

    kicad_project_path = os.path.relpath(prjctPath, gitRoot)

    return gitRoot, kicad_project_path
