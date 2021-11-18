import time
import os
import shutil
import sys
import settings
from scms.generic import scm as generic_scm


class scm(generic_scm):
    @staticmethod
    def get_boards(diff1, diff2, prjct_name, kicad_project_path, prjct_path):
        """Given two git artifacts, write out two kicad_pcb files to their respective
        directories (named after the artifact). Returns the date and time of both commits"""

        if not diff1 == prjct_name:
            artifact1 = diff1[:7]
        else:
            artifact1 = "local"

        if not diff2 == prjct_name:
            artifact2 = diff2[:7]
        else:
            artifact2 = "local"

        # Using this to fix the path when there is no subproject
        prj_path = kicad_project_path + "/"
        if kicad_project_path == ".":
            prj_path = ""

        if (not diff1 == prjct_name) and (not diff2 == prjct_name):
            cmd = ["git", "diff", "--name-only", artifact1, artifact2, "."]

            print("")
            print("Getting boards")
            print(' '.join(cmd))

            stdout, stderr = settings.run_cmd(prjct_path, cmd)
            changed = (prj_path + prjct_name) in stdout

            if not changed:
                print("\nThere is no difference in .kicad_pcb file in selected commits")

        outputDir1 = os.path.join(
            prjct_path, settings.output_dir, kicad_project_path, artifact1
        )
        if not os.path.exists(outputDir1):
            os.makedirs(outputDir1)

        outputDir2 = os.path.join(
            prjct_path, settings.output_dir, kicad_project_path, artifact2
        )
        if not os.path.exists(outputDir2):
            os.makedirs(outputDir2)

        gitPath = os.path.join(prj_path, prjct_name)

        print("")
        print("Setting artifacts paths")
        print("gitPath      :", gitPath)

        if not diff1 == prjct_name:
            gitArtifact1 = ["git", "show", artifact1 + ":" + gitPath]
            print("Git artifact1: ", ' '.join(gitArtifact1))
        else:
            print("Git artifact1: ", diff1)

        if not diff2 == prjct_name:
            gitArtifact2 = ["git", "show", artifact2 + ":" + gitPath]
            print("Git artifact2: ", ' '.join(gitArtifact2))
        else:
            print("Git artifact2: ", diff2)

        if not diff1 == prjct_name:
            stdout, stderr = settings.run_cmd(prjct_path, gitArtifact1)
            with open(os.path.join(outputDir1, prjct_name), "w") as fout1:
                fout1.write(stdout)
        else:
            shutil.copyfile(prjct_name, os.path.join(outputDir1, prjct_name))

        if not diff2 == prjct_name:
            stdout, stderr = settings.run_cmd(prjct_path, gitArtifact2)
            with open(os.path.join(outputDir2, prjct_name), "w") as fout2:
                fout2.write(stdout)
        else:
            shutil.copyfile(prjct_name, os.path.join(outputDir2, prjct_name))

        print("")
        print("Check datetime")

        if not diff1 == prjct_name:
            gitDateTime1 = ["git", "show", "-s", '--format="%ci"', artifact1]
            print(' '.join(gitDateTime1))

        if not diff2 == prjct_name:
            gitDateTime2 = ["git", "show", "-s", '--format="%ci"', artifact2]
            print(' '.join(gitDateTime2))

        if not diff1 == prjct_name:
            stdout, stderr = settings.run_cmd(prjct_path, gitDateTime1)
            dateTime1 = stdout
            date1, time1, UTC = dateTime1.split(" ")
            time1 = date1 + " " + time1
        else:
            artifact1 = prjct_name
            modTimesinceEpoc = os.path.getmtime(prjct_name)
            time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modTimesinceEpoc))

        if not diff2 == prjct_name:
            stdout, stderr = settings.run_cmd(prjct_path, gitDateTime2)
            dateTime2 = stdout
            date2, time2, UTC = dateTime2.split(" ")
            time2 = date2 + " " + time2
        else:
            artifact2 = prjct_name
            modTimesinceEpoc = os.path.getmtime(prjct_name)
            time2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modTimesinceEpoc))

        return artifact1, artifact2, time1 + " " + time2

    @staticmethod
    def get_artefacts(prjct_path, kicad_project_path, board_file):
        """Returns list of artifacts from a directory"""

        cmd = [
            "git",
            "log",
            "--date=local",
            "--pretty=format:%h | %ai | %an | %s",
            os.path.join(kicad_project_path, board_file),
        ]

        stdout, _ = settings.run_cmd(prjct_path, cmd)

        artifacts = [board_file] + stdout.splitlines()

        return artifacts

    @staticmethod
    def get_kicad_project_path(prjct_path):
        """Returns the root folder of the repository"""

        cmd = ["git", "rev-parse", "--show-toplevel"]

        stdout, _ = settings.run_cmd(prjct_path, cmd)
        repo_root_path = stdout.strip()

        kicad_project_path = os.path.relpath(prjct_path, repo_root_path)

        return repo_root_path, kicad_project_path
