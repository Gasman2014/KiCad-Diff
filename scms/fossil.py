import datetime
import os
import settings
import shutil
import sys
import time
from scms.generic import scm as generic_scm


class scm(generic_scm):

    @staticmethod
    def get_boards(kicad_pcb_path, repo_path, kicad_project_dir, board_filename, commit1, commit2):
        """Given two Fossil artifacts, write out two kicad_pcb files to their respective
        directories (named after the artifacts). Returns the date and time of both commits"""

        if not commit1 == board_filename:
            artifact1 = commit1[:6]
        else:
            artifact1 = "local"

        if not commit2 == board_filename:
            artifact2 = commit2[:6]
        else:
            artifact2 = "local"

        # Using this to fix the path when there is no subproject
        prj_path = kicad_project_dir + "/"
        if kicad_project_dir == ".":
            prj_path = ""

        if (not commit1 == board_filename) and (not commit2 == board_filename):

            cmd = ["fossil", "diff", "--brief", "-r", artifact1, "--to", artifact2]

            stdout, stderr = settings.run_cmd(repo_path, cmd)
            changed = ".kicad_pcb" in stdout

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

        fossilPath = os.path.join(prj_path, board_filename)

        if not commit1 == board_filename:
            fossilArtifact1 = [
                "fossil",
                "cat",
                repo_path + fossilPath,
                "-r",
                artifact1,
            ]

        if not commit2 == board_filename:
            fossilArtifact2 = [
                "fossil",
                "cat",
                repo_path + fossilPath,
                "-r",
                artifact2,
            ]

        if not commit1 == board_filename:
            fossilDateTime1 = ["fossil", "info", artifact1]

        else:
            artifact1 = board_filename
            modTimesinceEpoc = os.path.getmtime(kicad_pcb_path)
            dateDiff1 = time.strftime("%Y-%m-%d", time.localtime(modTimesinceEpoc))
            timeDiff1 = time.strftime("%H:%M:%S", time.localtime(modTimesinceEpoc))

        if not commit2 == board_filename:
            fossilDateTime2 = ["fossil", "info", artifact2]
        else:
            artifact2 = board_filename
            modTimesinceEpoc = os.path.getmtime(kicad_pcb_path)
            dateDiff2 = time.strftime("%Y-%m-%d", time.localtime(modTimesinceEpoc))
            timeDiff2 = time.strftime("%H:%M:%S", time.localtime(modTimesinceEpoc))

        if not commit1 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, fossilArtifact1)
            with open(os.path.join(outputDir1, board_filename), "w") as f:
                f.write(stdout)
            dateTime, _ = settings.run_cmd(repo_path, fossilDateTime1)
            (
                uuid,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                artifactRef,
                dateDiff1,
                timeDiff1,
                *junk1,
            ) = dateTime.split(" ")
        else:
            shutil.copyfile(kicad_pcb_path, os.path.join(outputDir1, board_filename))

        if not commit2 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, fossilArtifact2)
            with open(os.path.join(outputDir2, board_filename), "w") as f:
                f.write(stdout)
            dateTime, _ = settings.run_cmd(repo_path, fossilDateTime2)
            (
                uuid,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                _,
                artifactRef,
                dateDiff2,
                timeDiff2,
                *junk2,
            ) = dateTime.split(" ")
        else:
            shutil.copyfile(kicad_pcb_path, os.path.join(outputDir2, board_filename))

        dateTime = dateDiff1 + " " + timeDiff1 + " " + dateDiff2 + " " + timeDiff2

        return artifact1, artifact2, dateTime

    @staticmethod
    def get_artefacts(repo_path, kicad_project_dir, board_filename):
        """Returns list of artifacts from a directory"""

        cmd = ["fossil", "finfo", "-b", os.path.join(kicad_project_dir, board_filename)]

        stdout, stderr = settings.run_cmd(repo_path, cmd)
        artifacts = [board_filename] + [
            a.replace(" ", " | ", 4) for a in stdout.splitlines()
        ]

        return artifacts

    @staticmethod
    def split_repo_path(kicad_project_path):
        """Returns the root folder of the repository"""

        cmd = ["fossil", "status"]

        stdout, _ = settings.run_cmd(kicad_project_path, cmd)
        repo_path = stdout.split()[3]

        kicad_project_dir = os.path.relpath(kicad_project_path, repo_path)

        return repo_path, kicad_project_dir
