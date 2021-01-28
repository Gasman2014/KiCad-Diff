
import os
import sys

import subprocess
from subprocess import PIPE, STDOUT, Popen


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


def run_cmd(cmd):

    p = Popen(
        cmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True)

    stdout, stderr = p.communicate()
    p.wait()

    return stdout.decode('utf-8'), stderr.decode('utf-8')
