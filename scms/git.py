import time
import os
import shutil
import sys
import settings
from scms.generic import scm as generic_scm


class scm(generic_scm):

    @staticmethod
    def get_boards(repo_path, kicad_project_dir, board_filename, commit1, commit2):
        """Given two git artifacts, write out two kicad_pcb files to their respective
        directories (named after the artifact). Returns the date and time of both commits"""

        if not commit1 == board_filename:
            artifact1 = commit1[:7]
        else:
            artifact1 = "local"

        if not commit2 == board_filename:
            artifact2 = commit2[:7]
        else:
            artifact2 = "local"

        # Using this to fix the path when there is no subproject
        prj_path = kicad_project_dir + "/"
        if kicad_project_dir == ".":
            prj_path = ""

        if (not commit1 == board_filename) and (not commit2 == board_filename):
            cmd = ["git", "diff", "--name-only", artifact1, artifact2, "."]

            stdout, stderr = settings.run_cmd(repo_path, cmd)
            changed = (prj_path + board_filename) in stdout

            if not changed:
                print("\nThere is no difference in .kicad_pcb file in selected commits")

        outputDir1 = os.path.join(
            settings.output_dir, artifact1
        )
        if not os.path.exists(outputDir1):
            os.makedirs(outputDir1)

        outputDir2 = os.path.join(
            settings.output_dir, artifact2
        )
        if not os.path.exists(outputDir2):
            os.makedirs(outputDir2)

        board_subpath = os.path.join(prj_path, board_filename)

        if not commit1 == board_filename:
            gitArtifact1 = ["git", "show", artifact1 + ":" + board_subpath]

        if not commit2 == board_filename:
            gitArtifact2 = ["git", "show", artifact2 + ":" + board_subpath]

        if not commit1 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, gitArtifact1)
            with open(os.path.join(outputDir1, board_filename), "w") as fout1:
                fout1.write(stdout)
        else:
            shutil.copyfile(board_filename, os.path.join(outputDir1, board_filename))

        if not commit2 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, gitArtifact2)
            with open(os.path.join(outputDir2, board_filename), "w") as fout2:
                fout2.write(stdout)
        else:
            shutil.copyfile(board_filename, os.path.join(outputDir2, board_filename))

        if not commit1 == board_filename:
            gitDateTime1 = ["git", "show", "-s", '--format="%ci"', artifact1]

        if not commit2 == board_filename:
            gitDateTime2 = ["git", "show", "-s", '--format="%ci"', artifact2]

        if not commit1 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, gitDateTime1)
            dateTime1 = stdout
            date1, time1, UTC = dateTime1.split(" ")
            time1 = date1 + " " + time1
        else:
            artifact1 = board_filename
            modTimesinceEpoc = os.path.getmtime(board_filename)
            time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modTimesinceEpoc))

        if not commit2 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, gitDateTime2)
            dateTime2 = stdout
            date2, time2, UTC = dateTime2.split(" ")
            time2 = date2 + " " + time2
        else:
            artifact2 = board_filename
            modTimesinceEpoc = os.path.getmtime(board_filename)
            time2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modTimesinceEpoc))

        return artifact1, artifact2, time1 + " " + time2

    @staticmethod
    def get_artefacts(repo_path, kicad_project_dir, board_file):
        """Returns list of artifacts from a directory"""

        cmd = [
            "git",
            "log",
            "--date=local",
            "--pretty=format:%h | %ai | %an | %s",
            os.path.join(kicad_project_dir, board_file),
        ]

        stdout, _ = settings.run_cmd(repo_path, cmd)

        artifacts = [board_file] + stdout.splitlines()

        return artifacts

    @staticmethod
    def split_repo_path(kicad_project_path):
        """Returns the root folder of the repository"""

        cmd = ["git", "rev-parse", "--show-toplevel"]

        stdout, _ = settings.run_cmd(kicad_project_path, cmd)
        repo_path = stdout.strip()

        kicad_project_dir = os.path.relpath(kicad_project_path, repo_path)

        return repo_path, kicad_project_dir
