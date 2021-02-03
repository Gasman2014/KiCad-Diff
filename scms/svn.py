
import os
import sys

import subprocess
from subprocess import PIPE, STDOUT, Popen

import settings

def get_board_path(prjctName, prjctPath):

    # svnRootCmd = 'cd ' + settings.escape_string(prjctPath) + ' && svn rev-parse --show-toplevel'
    cmd = "echo [TODO]"

    print("")
    print("Getting SCM top level")
    print(cmd)

    stdout, stderr = settings.run_cmd(cmd)

    # svnPathCmd = 'cd ' + settings.escape_string(svnRoot) + ' && svn ls-tree -r --name-only HEAD | grep -m 1 ' + prjctName
    cmd = "echo [TODO]"

    print("")
    print("Getting board file")
    print(cmd)

    stdout, stderr = settings.run_cmd(cmd)

    return settings.escape_string(stdout)


def get_boards(diff1, diff2, prjctName, kicad_project_path, prjctPath):
    '''Given two SVN revisions, write out two kicad_pcb files to their respective
    directories (named after the revision number). Returns the date and time of both commits'''

    artifact1, *tail = diff1.split(' |')
    artifact2, *tail = diff2.split(' |')

    artifact1 = artifact1.replace(" ", "")
    artifact2 = artifact2.replace(" ", "")

    # Using this to fix the path when there is no subproject
    prj_path = kicad_project_path + '/'
    if kicad_project_path == '.':
        prj_path = ''

    cmd = 'cd ' + settings.escape_string(prjctPath) + ' && svn diff --summarize -r ' + \
        artifact1 + ':' + artifact2 + ' ' + prjctName

    print("")
    print("Getting Boards")
    print(cmd)

    stdout, stderr = settings.run_cmd(cmd)
    changed, *boardName = stdout

    if changed != 'M':
        print("\nThere is no difference in .kicad_pcb file in selected commits")
        sys.exit()

    outputDir1 = prjctPath + '/' + settings.plotDir + '/' + kicad_project_path + '/' + artifact1
    outputDir2 = prjctPath + '/' + settings.plotDir + '/' + kicad_project_path + '/' + artifact2

    if not os.path.exists(outputDir1):
        os.makedirs(outputDir1)

    if not os.path.exists(outputDir2):
        os.makedirs(outputDir2)

    svnArtifact1 = 'cd ' + prjctPath + ' && svn cat -r ' + artifact1 + \
        " " + prjctName + ' > ' + outputDir1 + '/' + prjctName

    svnArtifact2 = 'cd ' + prjctPath + ' && svn cat -r ' + artifact2 + \
        " " + prjctName + ' > ' + outputDir2 + '/' + prjctName

    print("")
    print("Get Artifacts")
    print(svnArtifact1)
    print(svnArtifact2)

    stdout, stderr = settings.run_cmd(svnArtifact1)
    stdout, stderr = settings.run_cmd(svnArtifact2)

    svnDateTime1 = 'cd ' + prjctPath + ' && svn log -r ' + artifact1
    svnDateTime2 = 'cd ' + prjctPath + ' && svn log -r ' + artifact2

    print("")
    print("Check datetime")
    print(svnDateTime1)
    print(svnDateTime2)

    stdout, stderr = settings.run_cmd(svnDateTime1)
    dateTime = stdout

    cmt = (dateTime.splitlines()[1]).split('|')
    _, SVNdate1, SVNtime1, SVNutc, *_ = cmt[2].split(' ')

    stdout, stderr = settings.run_cmd(svnDateTime2)
    dateTime = stdout

    cmt = (dateTime.splitlines()[1]).split('|')
    _, SVNdate2, SVNtime2, SVNutc, *_ = cmt[2].split(' ')

    times = SVNdate1 + " " + SVNtime1 + " " + SVNdate2 + " " + SVNtime2

    return artifact1, artifact2, times


def get_artefacts(prjctPath, board_file):
    '''Returns list of revisions from a directory'''

    cmd = 'cd {prjctPath} && svn log -r HEAD:0 | perl -l40pe "s/^-+/\\n/"'.format(prjctPath=prjctPath)

    print("")
    print("Getting Artifacts")
    print(cmd)

    stdout, stderr = settings.run_cmd(cmd)
    artifacts = stdout.splitlines()
    artifacts = list(filter(None, artifacts))

    return artifacts


def get_kicad_project_path(prjctPath):
    '''Returns the root folder of the repository'''

    cmd = "cd {prjctPath} && svn info --show-item wc-root".format(
        prjctPath=settings.escape_string(prjctPath))

    stdout, _ = settings.run_cmd(cmd)
    repo_root_path = stdout.strip()

    kicad_project_path = os.path.relpath(prjctPath, repo_root_path)

    return repo_root_path, kicad_project_path