import sys

from subprocess import PIPE, Popen
from typing import List, Tuple

args = ""

global verbose

global gitProg
global fossilProg
global svnProg
global diffProg
global grepProg

global plot_prog

global output_dir
global web_dir

verbose = 0

gitProg = "git"
fossilProg = "fossil"
svnProg = "svn"
diffProg = "diff"
grepProg = "grep"

plot_prog = "plotpcb"

web_dir = "web"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run_cmd(exec_path: str, cmd: List[str]) -> Tuple[str, str]:

    if verbose > 1:
        print("")
        print(bcolors.WARNING + "Path:", exec_path + bcolors.ENDC)
        print(bcolors.WARNING + " Cmd:", bcolors.OKBLUE + " ".join(cmd) + bcolors.ENDC)

    p = Popen(
        cmd,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True,
        encoding="utf-8",
        cwd=exec_path,
    )

    stdout, stderr = p.communicate()
    p.wait()

    if verbose > 3:
        print(bcolors.OKCYAN + stdout + bcolors.ENDC)

    if verbose > 1:
        print(bcolors.FAIL + stderr + bcolors.ENDC)

    return stdout.strip("\n "), stderr
