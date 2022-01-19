#!/usr/bin/env python

from __future__ import print_function
import pcbnew
import wx
import platform
import os
import sys
import subprocess
import pathlib
import signal
import atexit

CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008


class kidiff(pcbnew.ActionPlugin):

    process = []

    def defaults(self):
        self.name = "KiCad Diff (kidiff)"
        self.category = "Revision"
        self.description = "Kicad PCB Layout Diff"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./kidiff.png")

    def Run(self):

        atexit.register(self.exit_handler)

        if self.process:
            for p in self.process:
                if not p.poll():
                    print("Terminating kidiff process (pid={})".format(p.pid))
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                self.process.remove(p)

        project_path = os.environ.get('KIPRJMOD')
        board = pcbnew.GetBoard()
        project_file_path = os.path.join(project_path, board.GetFileName())
        cmd = ['kidiff', project_file_path]

        kwargs = {}
        if platform.system() == 'Windows':
            CREATE_NEW_PROCESS_GROUP = 0x00000200  # note: could get it from subprocess
            DETACHED_PROCESS = 0x00000008          # 0x8 | 0x200 == 0x208
            kwargs.update(creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
        elif sys.version_info < (3, 2):  # assume posix
            kwargs.update(preexec_fn=os.setsid)
        else:  # Python 3.2+ and Unix
            kwargs.update(start_new_session=True)

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        self.process.append(process)
        print("kidiff (pid={})".format(process.pid))
        assert not process.poll()

    def exit_handler(self):
        if self.process:
            for p in self.process:
                if not p.poll():
                    print("Terminating kidiff process (pid={})".format(p.pid))
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                self.process.remove(p)


kidiff().register()
