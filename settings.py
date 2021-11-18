import sys

from subprocess import PIPE, Popen
from typing import List, Tuple

args = ""

global gitProg
global fossilProg
global svnProg
global diffProg
global grepProg

global plot_prog

global output_dir
global web_dir

gitProg = "git"
fossilProg = "fossil"
svnProg = "svn"
diffProg = "diff"
grepProg = "grep"

plot_prog = "plotpcb"

# output_dir = "kidiff"
web_dir = "web"


def run_cmd(path: str, cmd: List[str]) -> Tuple[str, str]:

    p = Popen(
        cmd,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True,
        encoding="utf-8",
        cwd=path,
    )

    stdout, stderr = p.communicate()
    p.wait()

    return stdout.strip("\n "), stderr
