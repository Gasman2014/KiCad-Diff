
import sys

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
