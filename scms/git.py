
import os
import sys
import settings
from scms.generic import scm as generic_scm

class scm(generic_scm):
    @staticmethod
    def get_boards(diff1, diff2, prjctName, kicad_project_path, prjctPath):
        '''Given two git artifacts, write out two kicad_pcb files to their respective
        directories (named after the artifact). Returns the date and time of both commits'''

        artifact1 = diff1[:7]
        artifact2 = diff2[:7]

        # Using this to fix the path when there is no subproject
        prj_path = kicad_project_path + '/'
        if kicad_project_path == '.':
            prj_path = ''

        cmd = ['git', 'diff', '--name-only', artifact1, artifact2, '.']

        print("")
        print("Getting boards")
        print(cmd)

        stdout, stderr = settings.run_cmd(prjctPath, cmd)
        changed = (prj_path + prjctName) in stdout

        if not changed:
            print("\nThere is no difference in .kicad_pcb file in selected commits")
            sys.exit()

        outputDir1 = os.path.join(prjctPath, settings.plotDir, kicad_project_path, artifact1)
        outputDir2 = os.path.join(prjctPath, settings.plotDir, kicad_project_path, artifact2)

        if not os.path.exists(outputDir1):
            os.makedirs(outputDir1)

        if not os.path.exists(outputDir2):
            os.makedirs(outputDir2)


        gitPath = prj_path + prjctName

        gitArtifact1 = ['git', 'show', artifact1 + ':' + gitPath]
        gitArtifact2 = ['git', 'show', artifact2 + ':' + gitPath]

        print("")
        print("Get artifacts")
        print("gitPath      :", gitPath)
        print("Git artifact1: ", gitArtifact1)
        print("Git artifact2: ", gitArtifact2)

        stdout, stderr = settings.run_cmd(prjctPath, gitArtifact1)
        with open(os.path.join(outputDir1, prjctName), 'w') as fout1:
            fout1.write(stdout)
        stdout, stderr = settings.run_cmd(prjctPath, gitArtifact2)
        with open(os.path.join(outputDir2, prjctName), 'w') as fout2:
            fout2.write(stdout)
        gitDateTime1 = ['git', 'show', '-s', '--format="%ci"', artifact1]
        gitDateTime2 = ['git', 'show', '-s', '--format="%ci"', artifact2]

        print("")
        print("Check datetime")
        print(gitDateTime1)
        print(gitDateTime2)

        stdout, stderr = settings.run_cmd(prjctPath, gitDateTime1)
        dateTime1 = stdout
        date1, time1, UTC = dateTime1.split(' ')

        stdout, stderr = settings.run_cmd(prjctPath, gitDateTime2)
        dateTime2 = stdout
        date2, time2, UTC = dateTime2.split(' ')

        time1 = date1 + " " + time1
        time2 = date2 + " " + time2

        return artifact1, artifact2, time1 + " " + time2

    @staticmethod
    def get_artefacts(prjctPath, kicad_project_path, board_file):
        '''Returns list of artifacts from a directory'''

        cmd = ['git', 'log', '--date=local', '--pretty=format:%h | %ai | %an | %s', os.path.join(kicad_project_path, board_file)]

        stdout, _ = settings.run_cmd(prjctPath, cmd)

        artifacts = stdout.splitlines()

        return artifacts

    @staticmethod
    def get_kicad_project_path(prjctPath):
        '''Returns the root folder of the repository'''

        cmd = ['git', 'rev-parse', '--show-toplevel']

        stdout, _ = settings.run_cmd(prjctPath, cmd)
        repo_root_path = stdout.strip()

        kicad_project_path = os.path.relpath(prjctPath, repo_root_path)

        return repo_root_path, kicad_project_path
