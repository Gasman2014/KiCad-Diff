import time
import os
import shutil
import sys
import settings
from scms.generic import scm as generic_scm
from xml.parsers.expat import ParserCreate
import xml.etree.ElementTree as et
from datetime import datetime

class scm(generic_scm):

    @staticmethod
    def get_boards(kicad_pcb_path, repo_path, kicad_project_dir, board_filename, commit1, commit2):
        """Given two SVN revisions, write out two kicad_pcb files to their respective
        directories (named after the revision number). Returns the date and time of both commits"""

        if not commit1 == board_filename:
            artifact1, *tail = commit1.split(" |")
        else:
            artifact1 = "local"

        if not commit2 == board_filename:
            artifact2, *tail = commit2.split(" |")
        else:
            artifact2 = "local"

        # Using this to fix the path when there is no subproject
        prj_path = kicad_project_dir + "/"
        if kicad_project_dir == ".":
            prj_path = ""

        if (not commit1 == board_filename) and (not commit2 == board_filename):
            cmd = ["svn", "diff", "--summarize", "-r", artifact1 + ":" + artifact2, prj_path + board_filename,]

            stdout, stderr = settings.run_cmd(repo_path, cmd)
            changed, *boardName = stdout

            if changed != "M":
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
            svnArtifact1 = ["svn", "cat", "-r", artifact1, board_subpath]

        if not commit2 == board_filename:
            svnArtifact2 = ["svn", "cat", "-r", artifact2, board_subpath]

        if not commit1 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, svnArtifact1)
            with open(os.path.join(outputDir1, board_filename), "w") as fout1:
                fout1.write(stdout)
        else:
            shutil.copyfile(kicad_pcb_path, os.path.join(outputDir1, board_filename))

        if not commit2 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, svnArtifact2)
            with open(os.path.join(outputDir2, board_filename), "w") as fout2:
                fout2.write(stdout)
        else:
            shutil.copyfile(kicad_pcb_path, os.path.join(outputDir2, board_filename))

        if not commit1 == board_filename:
            svnDateTime1 = ["svn", "log", "-r", artifact1]

        if not commit2 == board_filename:
            svnDateTime2 = ["svn", "log", "-r", artifact2]

        if not commit1 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, svnDateTime1)
            dateTime = stdout
            cmt = (dateTime.splitlines()[1]).split("|")
            _, SVNdate1, SVNtime1, SVNutc, *_ = cmt[2].split(" ")
        else:
            artifact1 = board_filename
            modTimesinceEpoc = os.path.getmtime(kicad_pcb_path)
            SVNdate1 = time.strftime("%Y-%m-%d", time.localtime(modTimesinceEpoc))
            SVNtime1 = time.strftime("%H:%M:%S", time.localtime(modTimesinceEpoc))

        time1 = SVNdate1 + " " + SVNtime1

        if not commit2 == board_filename:
            stdout, stderr = settings.run_cmd(repo_path, svnDateTime2)
            dateTime = stdout

            cmt = (dateTime.splitlines()[1]).split("|")
            _, SVNdate2, SVNtime2, SVNutc, *_ = cmt[2].split(" ")
        else:
            artifact2 = board_filename
            modTimesinceEpoc = os.path.getmtime(kicad_pcb_path)
            SVNdate2 = time.strftime("%Y-%m-%d", time.localtime(modTimesinceEpoc))
            SVNtime2 = time.strftime("%H:%M:%S", time.localtime(modTimesinceEpoc))

        time2 = SVNdate2 + " " + SVNtime2

        return artifact1, artifact2, time1 + " " + time2

    @staticmethod
    def get_pages(kicad_sch_path, repo_path, kicad_project_dir, page_filename, commit1, commit2):
        """Given two svn artifacts, write out two sets of kicad_sch files to their respective
        directories (named after the artifact). Returns the date and time of both commits"""
        
        print("")
        print("***HERE***")
        print("")
        
        if commit1 == "local":
            commit1 = page_filename
        
        if commit2 == "local":
            commit2 = page_filename
        
        isLocal1 = commit1 == page_filename
        isLocal2 = commit2 == page_filename
        
        artifact1 = "local" if isLocal1 else commit1.split(" ")[0]
        artifact2 = "local" if isLocal2 else commit2.split(" ")[0]
        
        # Fix the path when there is no subproject
        prj_path = kicad_project_dir + "/"
        if kicad_project_dir == ".":
            prj_path = ""
        
        if (not isLocal1) and (not isLocal2):
            # TODO: only checks top level sheet, so worse than not having the check at the moment.
            #       But we go on anyway (return is commented out), because the caller needs the
            #       files regardless. So the only effect is a print message.
            cmd = ["svn", "diff", "--summarize", "-r", artifact1 + ":" + artifact2, kicad_sch_path,]
            stdout, stderr = settings.run_cmd(repo_path, cmd)
            if len(stdout) > 1:
                changed, *boardName = stdout
            else:
                changed = ""
            
            if changed != "M":
                print("\nThere is no difference in .kicad_sch file in selected commits")
                #return
        
        outputDir1 = os.path.join(settings.output_dir, artifact1)
        outputDir2 = os.path.join(settings.output_dir, artifact2)
        if not os.path.exists(outputDir1):
            os.makedirs(outputDir1)
        if not os.path.exists(outputDir2):
            os.makedirs(outputDir2)
        
        page_subpath = os.path.join(prj_path, page_filename)
        
        if not isLocal1:
            svnArtifact1 = ["svn", "cat", "-r", artifact1, page_subpath]
            stdout, stderr = settings.run_cmd(repo_path, svnArtifact1)
            with open(os.path.join(outputDir1, page_filename), "w") as fout1:
                fout1.write(stdout)
            # svnDateTime1 = ["svn", "log", "-r", artifact1]
            # stdout, stderr = settings.run_cmd(repo_path, svnDateTime1)
            # print(stdout)
        else:
            shutil.copyfile(kicad_sch_path, os.path.join(outputDir1, page_filename))
        
        if not isLocal2:
            svnArtifact1 = ["svn", "cat", "-r", artifact2, page_subpath]
            stdout, stderr = settings.run_cmd(repo_path, svnArtifact1)
            with open(os.path.join(outputDir2, page_filename), "w") as fout2:
                fout2.write(stdout)
            # svnDateTime2 = ["svn", "log", "-r", artifact2]
            # stdout, stderr = settings.run_cmd(repo_path, svnDateTime2)
            # print(stdout)
        else:
            shutil.copyfile(kicad_sch_path, os.path.join(outputDir2, page_filename))
    
    @staticmethod
    def get_artefacts(repo_path, kicad_project_dir, board_filename):
        """Returns list of revisions from a directory"""

        cmd = ["svn", "log", "--xml", "-r", "HEAD:0", os.path.join(kicad_project_dir, board_filename)]
        stdout, _ = settings.run_cmd(repo_path, cmd)

        root = et.fromstring(stdout)
        commits = []

        for entry in root.findall('./logentry'):
            rev = entry.attrib['revision']
            try:
                author_str = entry.find('author').text
            except:
                author_str = "[author]"
            date_str = entry.find('date').text
            date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            date = date_obj.strftime("%Y-%m-%d %H:%M")
            msg_str = entry.find('msg').text if entry.find('msg').text else "[Message]"
            artifact = "{} | {} | {} | {}".format(rev, date, author_str, msg_str)
            commits.append(artifact)

        artifacts = [board_filename] + commits

        return artifacts

    @staticmethod
    def split_repo_path(kicad_project_path):
        """Returns the root folder of the repository"""

        cmd = ["svn", "info", "--show-item", "wc-root"]
        stdout, _ = settings.run_cmd(kicad_project_path, cmd)
        repo_path = stdout.strip()

        kicad_project_dir = os.path.relpath(kicad_project_path, repo_path)

        return repo_path, kicad_project_dir
