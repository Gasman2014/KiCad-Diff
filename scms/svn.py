
import os
import sys
import settings
from scms.generic import scm as generic_scm
from xml.parsers.expat import ParserCreate
import datetime
from dateutil.parser import isoparse

class scm(generic_scm):
    @staticmethod
    def get_boards(diff1, diff2, prjctName, kicad_project_path, prjctPath):
        '''Given two SVN revisions, write out two kicad_pcb files to their respective
        directories (named after the revision number). Returns the date and time of both commits'''

        artifact1, *tail = diff1.split(' |')
        artifact2, *tail = diff2.split(' |')


        # Using this to fix the path when there is no subproject
        prj_path = kicad_project_path + '/'
        if kicad_project_path == '.':
            prj_path = ''

        cmd = ['svn', 'diff', '--summarize', '-r', artifact1 + ':' + artifact2, prj_path + prjctName]

        print("")
        print("Getting Boards")
        print(cmd)

        stdout, stderr = settings.run_cmd(prjctPath, cmd)
        changed, *boardName = stdout

        if changed != 'M':
            print("\nThere is no difference in .kicad_pcb file in selected commits")
            sys.exit()

        outputDir1 = os.path.join(prjctPath, settings.plotDir, kicad_project_path, artifact1)
        outputDir2 = os.path.join(prjctPath, settings.plotDir, kicad_project_path, artifact2)

        if not os.path.exists(outputDir1):
            os.makedirs(outputDir1)

        if not os.path.exists(outputDir2):
            os.makedirs(outputDir2)

        gitPath = prj_path + prjctName

        svnArtifact1 = ['svn', 'cat', '-r', artifact1, gitPath]
        svnArtifact2 = ['svn', 'cat', '-r', artifact2, gitPath]

        print("")
        print("Get Artifacts")
        print(svnArtifact1)
        print(svnArtifact2)

        stdout, stderr = settings.run_cmd(prjctPath, svnArtifact1)
        with open(os.path.join(outputDir1, prjctName), 'w') as fout1:
            fout1.write(stdout)
        stdout, stderr = settings.run_cmd(prjctPath, svnArtifact2)
        with open(os.path.join(outputDir2, prjctName), 'w') as fout2:
            fout2.write(stdout)

        svnDateTime1 = ['svn', 'log', '-r', artifact1]
        svnDateTime2 = ['svn', 'log', '-r', artifact2]

        print("")
        print("Check datetime")
        print(svnDateTime1)
        print(svnDateTime2)

        stdout, stderr = settings.run_cmd(prjctPath, svnDateTime1)
        dateTime = stdout

        cmt = (dateTime.splitlines()[1]).split('|')
        _, SVNdate1, SVNtime1, SVNutc, *_ = cmt[2].split(' ')

        stdout, stderr = settings.run_cmd(prjctPath, svnDateTime2)
        dateTime = stdout

        cmt = (dateTime.splitlines()[1]).split('|')
        _, SVNdate2, SVNtime2, SVNutc, *_ = cmt[2].split(' ')

        times = SVNdate1 + " " + SVNtime1 + " " + SVNdate2 + " " + SVNtime2

        return artifact1, artifact2, times

    @staticmethod
    def get_artefacts(prjctPath, kicad_project_path, board_file):
        '''Returns list of revisions from a directory'''

        cmd = ['svn', 'log', '--xml', '-r', 'HEAD:0', os.path.join(kicad_project_path, board_file)]
        print("")
        print("Getting Artifacts")
        print(cmd)

        stdout, _ = settings.run_cmd(prjctPath, cmd)
        parser = SvnLogHandler()
        parser.parseString(stdout)
        artifacts = parser.lines

        return artifacts

    @staticmethod
    def get_kicad_project_path(prjctPath):
        '''Returns the root folder of the repository'''

        cmd = ['svn', 'info', '--show-item', 'wc-root']

        stdout, _ = settings.run_cmd(prjctPath, cmd)
        repo_root_path = stdout.strip()

        kicad_project_path = os.path.relpath(prjctPath, repo_root_path)

        return repo_root_path, kicad_project_path


class SvnLogHandler:

    def __init__(self):
        self.parser = ParserCreate()
        self.parser.StartElementHandler = self.startElement
        self.parser.EndElementHandler = self.endElement
        self.parser.CharacterDataHandler = self.characters
        self.lines = []
        self.current_line = ""
        self.save = False

    def parseString(self, data):
        self.parser.Parse(data)

    def startElement(self, name, attrs):
        if name == "logentry":
            self.current_line = "r" + attrs.get('revision')

        else:
            self.save = name == "date" or name == "msg"
        if self.save:
            self.save = name
            self.current_line += " | "

    def endElement(self, name):
        if name == "logentry":
            self.lines.append(self.current_line)

    def characters(self, content):
        if self.save and len(content):
            if self.save == "date":
                self.current_line += isoparse(content).strftime("%Y-%m-%d %H:%M")
            else:
                self.current_line += content
            self.save = False
