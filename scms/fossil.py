import datetime
import os
import settings
import shutil
import sys
import time
from scms.generic import scm as generic_scm


class scm(generic_scm):
    @staticmethod
    def get_boards(diff1, diff2, prjct_name, kicad_project_path, prjct_path):
        """Given two Fossil artifacts, write out two kicad_pcb files to their respective
        directories (named after the artifacts). Returns the date and time of both commits"""

        if not diff1 == prjct_name:
            artifact1 = diff1[:6]
        else:
            artifact1 = "local"

        if not diff2 == prjct_name:
            artifact2 = diff2[:6]
        else:
            artifact2 = "local"

        # Using this to fix the path when there is no subproject
        prj_path = os.path.join(kicad_project_path, "/")
        if kicad_project_path == ".":
            prj_path = ""

        if (not diff1 == prjct_name) and (not diff2 == prjct_name):

            cmd = ["fossil", "diff", "--brief", "-r", artifact1, "--to", artifact2]

            print("")
            print("Getting Boards")
            print(' '.join(cmd))

            stdout, stderr = settings.run_cmd(prjct_path, cmd)
            changed = ".kicad_pcb" in stdout

            if not changed:
                print("\nThere is no difference in .kicad_pcb file in selected commits")

        outputDir1 = os.path.join(
            prjct_path, settings.plot_dir, kicad_project_path, artifact1
        )
        if not os.path.exists(outputDir1):
            os.makedirs(outputDir1)

        outputDir2 = os.path.join(
            prjct_path, settings.plot_dir, kicad_project_path, artifact2
        )
        if not os.path.exists(outputDir2):
            os.makedirs(outputDir2)

        print("")
        print("Setting output paths")
        print(outputDir1)
        print(outputDir2)

        fossilPath = os.path.join(prj_path, prjct_name)

        print("")
        print("Setting artifacts paths")
        print("fossilPath   :", fossilPath)

        if not diff1 == prjct_name:
            fossilArtifact1 = [
                "fossil",
                "cat",
                prjct_path + fossilPath,
                "-r",
                artifact1,
            ]
            print("Fossil artifact2: ", fossilArtifact1)
        else:
            print("Fossil artifact2: ", diff1)

        if not diff2 == prjct_name:
            fossilArtifact2 = [
                "fossil",
                "cat",
                prjct_path + fossilPath,
                "-r",
                artifact2,
            ]
            print("Fossil artifact2: ", fossilArtifact2)
        else:
            print("Fossil artifact2: ", diff2)

        print("")
        print("Checking datetime")

        if not diff1 == prjct_name:
            fossilDateTime1 = ["fossil", "info", artifact1]
            print(' '.join(fossilDateTime1))

        else:
            artifact1 = prjct_name
            modTimesinceEpoc = os.path.getmtime(prjct_name)
            dateDiff1 = time.strftime("%Y-%m-%d", time.localtime(modTimesinceEpoc))
            timeDiff1 = time.strftime("%H:%M:%S", time.localtime(modTimesinceEpoc))

        if not diff2 == prjct_name:
            fossilDateTime2 = ["fossil", "info", artifact2]
            print(' '.join(fossilDateTime2))
        else:
            artifact2 = prjct_name
            modTimesinceEpoc = os.path.getmtime(prjct_name)
            dateDiff2 = time.strftime("%Y-%m-%d", time.localtime(modTimesinceEpoc))
            timeDiff2 = time.strftime("%H:%M:%S", time.localtime(modTimesinceEpoc))

        if not diff1 == prjct_name:
            stdout, stderr = settings.run_cmd(prjct_path, fossilArtifact1)
            with open(os.path.join(outputDir1, prjct_name), "w") as f:
                f.write(stdout)
            dateTime, _ = settings.run_cmd(prjct_path, fossilDateTime1)
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
            shutil.copyfile(prjct_name, os.path.join(outputDir1, prjct_name))

        if not diff2 == prjct_name:
            stdout, stderr = settings.run_cmd(prjct_path, fossilArtifact2)
            with open(os.path.join(outputDir2, prjct_name), "w") as f:
                f.write(stdout)
            dateTime, _ = settings.run_cmd(prjct_path, fossilDateTime2)
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
            shutil.copyfile(prjct_name, os.path.join(outputDir2, prjct_name))

        dateTime = dateDiff1 + " " + timeDiff1 + " " + dateDiff2 + " " + timeDiff2

        return artifact1, artifact2, dateTime

    @staticmethod
    def get_artefacts(prjct_path, kicad_project_path, board_file):
        """Returns list of artifacts from a directory"""

        cmd = ["fossil", "finfo", "-b", os.path.join(kicad_project_path, board_file)]

        print("")
        print("Getting artifacts")
        print(cmd)

        stdout, stderr = settings.run_cmd(prjct_path, cmd)
        artifacts = [board_file] + [
            a.replace(" ", " | ", 4) for a in stdout.splitlines()
        ]

        return artifacts

    @staticmethod
    def get_kicad_project_path(prjct_path):
        """Returns the root folder of the repository"""

        cmd = ["fossil", "status"]

        stdout, _ = settings.run_cmd(prjct_path, cmd)
        repo_root_path = stdout.split()[3]

        kicad_project_path = os.path.relpath(prjct_path, repo_root_path)

        return repo_root_path, kicad_project_path
