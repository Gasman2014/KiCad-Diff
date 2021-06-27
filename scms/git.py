
import time
import os
import shutil
import sys
import settings
from scms.generic import scm as generic_scm

class scm(generic_scm):
    @staticmethod
    def get_boards(diff1, diff2, prjctName, kicad_project_path, prjctPath):
        '''Given two git artifacts, write out two kicad_pcb files to their respective
        directories (named after the artifact). Returns the date and time of both commits'''

        if not diff1 == prjctName:
            artifact1 = diff1[:7]
        else:
            artifact1 = "local"

        if not diff2 == prjctName:
            artifact2 = diff2[:7]
        else:
            artifact2 = "local"

        # Using this to fix the path when there is no subproject
        prj_path = kicad_project_path + '/'
        if kicad_project_path == '.':
            prj_path = ''

        if (not diff1 == prjctName) and (not diff2 == prjctName):
            cmd = ['git', 'diff', '--name-only', artifact1, artifact2, '.']

            print("")
            print("Getting boards")
            print(cmd)

            stdout, stderr = settings.run_cmd(prjctPath, cmd)
            changed = (prj_path + prjctName) in stdout

            if not changed:
                print("\nThere is no difference in .kicad_pcb file in selected commits")

        outputDir1 = os.path.join(prjctPath, settings.plotDir, kicad_project_path, artifact1)
        if not os.path.exists(outputDir1):
            os.makedirs(outputDir1)

        outputDir2 = os.path.join(prjctPath, settings.plotDir, kicad_project_path, artifact2)
        if not os.path.exists(outputDir2):
            os.makedirs(outputDir2)

        gitPath = prj_path + prjctName

        print("")
        print("Setting artifacts paths")
        print("gitPath      :", gitPath)

        if not diff1 == prjctName:
            gitArtifact1 = ['git', 'show', artifact1 + ':' + gitPath]
            print("Git artifact1: ", gitArtifact1)
        else:
            print("Git artifact1: ", diff1)

        if not diff2 == prjctName:
            gitArtifact2 = ['git', 'show', artifact2 + ':' + gitPath]
            print("Git artifact2: ", gitArtifact2)
        else:
            print("Git artifact2: ", diff2)

        if not diff1 == prjctName:
            stdout, stderr = settings.run_cmd(prjctPath, gitArtifact1)
            with open(os.path.join(outputDir1, prjctName), 'w') as fout1:
                fout1.write(stdout)
        else:
            shutil.copyfile(prjctName, os.path.join(outputDir1, prjctName))


        if not diff2 == prjctName:
            stdout, stderr = settings.run_cmd(prjctPath, gitArtifact2)
            with open(os.path.join(outputDir2, prjctName), 'w') as fout2:
                fout2.write(stdout)
        else:
            shutil.copyfile(prjctName, os.path.join(outputDir1, prjctName))

        print("")
        print("Check datetime")

        if not diff1 == prjctName:
            gitDateTime1 = ['git', 'show', '-s', '--format="%ci"', artifact1]
            print(gitDateTime1)

        if not diff2 == prjctName:
            gitDateTime2 = ['git', 'show', '-s', '--format="%ci"', artifact2]
            print(gitDateTime2)

        if not diff1 == prjctName:
            stdout, stderr = settings.run_cmd(prjctPath, gitDateTime1)
            dateTime1 = stdout
            date1, time1, UTC = dateTime1.split(' ')
            time1 = date1 + " " + time1
        else:
            artifact1 = prjctName
            modTimesinceEpoc = os.path.getmtime(prjctName)
            time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))

        if not diff2 == prjctName:
            stdout, stderr = settings.run_cmd(prjctPath, gitDateTime2)
            dateTime2 = stdout
            date2, time2, UTC = dateTime2.split(' ')
            time2 = date2 + " " + time2
        else:
            artifact2 = prjctName
            modTimesinceEpoc = os.path.getmtime(prjctName)
            time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))

        return artifact1, artifact2, time1 + " " + time2

    @staticmethod
    def get_artefacts(prjctPath, kicad_project_path, board_file):
        '''Returns list of artifacts from a directory'''

        cmd = ['git', 'log', '--date=local', '--pretty=format:%h | %ai | %an | %s', os.path.join(kicad_project_path, board_file)]

        stdout, _ = settings.run_cmd(prjctPath, cmd)

        artifacts = [board_file] + stdout.splitlines()

        return artifacts

    @staticmethod
    def get_kicad_project_path(prjctPath):
        '''Returns the root folder of the repository'''

        cmd = ['git', 'rev-parse', '--show-toplevel']

        stdout, _ = settings.run_cmd(prjctPath, cmd)
        repo_root_path = stdout.strip()

        kicad_project_path = os.path.relpath(prjctPath, repo_root_path)

        return repo_root_path, kicad_project_path
