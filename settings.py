
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


def escape_string(val):

    if sys.version_info[0] >= 3:
        unicode = str

    val = unicode(val)
    val = val.replace( u'\\', u'\\\\' )
    val = val.replace( u' ', u'\\ ' )

    return ''.join(val.splitlines())


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
