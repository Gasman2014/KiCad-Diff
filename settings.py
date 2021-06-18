
import sys

from subprocess import PIPE, Popen
from typing import List, Tuple

args = ''

global gitProg
global fossilProg
global svnProg
global diffProg
global grepProg

global plotProg

global plotDir
global webDir

gitProg = 'git'
fossilProg = 'fossil'
svnProg = 'svn'
diffProg = 'diff'
grepProg = 'grep'

plotProg = 'plotpcb'

plotDir = 'kidiff'
webDir = 'web'


def run_cmd(path: str, cmd: List[str]) -> Tuple[str, str]:

    p = Popen(
        cmd,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True,
        encoding='utf-8',
        cwd=path)

    stdout, stderr = p.communicate()
    p.wait()

    return stdout.strip("\n "), stderr
