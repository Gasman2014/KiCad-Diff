
import os
import sys
import settings
from scms.generic import scm as generic_scm

class scm(generic_scm):
    @staticmethod
    def get_board_path(prjctName, prjctPath):

        # cmd = 'cd ' + settings.escape_string(prjctPath) + ' && fossil rev-parse --show-toplevel'
        cmd = "todo"

        stdout, stderr = settings.run_cmd(cmd)
        scm_root = stdout

        # cmd = 'cd ' + settings.escape_string(scm_root) + ' && fossil ls-tree -r --name-only HEAD | grep -m 1 ' + prjctName
        cmd = "todo"

        stdout, stderr = settings.run_cmd(cmd)

        return settings.escape_string(stdout)

    @staticmethod
    def get_boards(diff1, diff2, prjctName, kicad_project_path, prjctPath):
        '''Given two Fossil artifacts, write out two kicad_pcb files to their respective
        directories (named after the artifacts). Returns the date and time of both commits'''

        artifact1 = diff1[:6]
        artifact2 = diff2[:6]

        cmd = 'cd ' + settings.escape_string(prjctPath) + ' && fossil diff --brief -r ' + \
            artifact1 + ' --to ' + artifact2 + ' | grep .kicad_pcb'

        print("")
        print("Getting Boards")
        print(cmd)

        stdout, stderr = settings.run_cmd(cmd)
        changed = stdout

        if changed == '':
            print("\nThere is no difference in .kicad_pcb file in selected commits")
            sys.exit()

        outputDir1 = prjctPath + settings.plotDir + '/' + artifact1
        outputDir2 = prjctPath + settings.plotDir + '/' + artifact2

        if not os.path.exists(outputDir1):
            os.makedirs(outputDir1)

        if not os.path.exists(outputDir2):
            os.makedirs(outputDir2)

        print("")
        print("Setting output paths")
        print(outputDir1)
        print(outputDir2)

        fossilArtifact1 = 'cd ' + settings.escape_string(prjctPath) + ' && fossil cat ' + settings.escape_string(prjctPath) + prjctName + \
            ' -r ' + artifact1 + ' > ' + outputDir1 + '/' + prjctName

        fossilArtifact2 = 'cd ' + settings.escape_string(prjctPath) + ' && fossil cat ' + settings.escape_string(prjctPath) + prjctName + \
            ' -r ' + artifact2 + ' > ' + outputDir2 + '/' + prjctName

        print("")
        print("Setting artifact paths")
        print(fossilArtifact1)
        print(fossilArtifact2)

        fossilDateTime1 = 'cd ' + settings.escape_string(prjctPath) + ' && fossil info ' + artifact1
        fossilDateTime2 = 'cd ' + settings.escape_string(prjctPath) + ' && fossil info ' + artifact2

        print("")
        print("Checking datetime")
        print(fossilDateTime1)
        print(fossilDateTime2)

        stdout, stderr = settings.run_cmd(fossilArtifact1)
        dateTime, _ = settings.run_cmd(fossilDateTime1)
        uuid, _, _, _, _, _, _, _, _, artifactRef, dateDiff1, timeDiff1, *junk1 = dateTime.split(" ")

        stdout, stderr = settings.run_cmd(fossilArtifact2)
        dateTime, _ = settings.run_cmd(fossilDateTime2)
        uuid, _, _, _, _, _, _, _, _, artifactRef, dateDiff2, timeDiff2, *junk2 = dateTime.split(" ")

        dateTime = dateDiff1 + " " + timeDiff1 + " " + dateDiff2 + " " + timeDiff2

        return artifact1, artifact2, dateTime

    @staticmethod
    def get_artefacts(prjctPath, board_file):
        '''Returns list of artifacts from a directory'''

        cmd = 'cd {prjctPath} && fossil finfo -b {board_file}'.format(prjctPath=prjctPath, board_file=board_file)

        print("")
        print("Getting artifacts")
        print(cmd)

        stdout, stderr = settings.run_cmd(cmd)
        artifacts = [a.replace(' ', ' | ', 4) for a in stdout.splitlines()]

        return artifacts

    @staticmethod
    def get_kicad_project_path(prjctPath):
        '''Returns the root folder of the repository'''

        cmd = "cd {prjctPath} && fossil status ".format(
            prjctPath=settings.escape_string(prjctPath))

        stdout, _ = settings.run_cmd(cmd)
        repo_root_path = stdout.split()[3]

        kicad_project_path = os.path.relpath(prjctPath, repo_root_path)

        return repo_root_path, kicad_project_path
