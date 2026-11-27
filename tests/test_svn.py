import shutil
import subprocess

import pytest

from scms.svn import scm


pytestmark = pytest.mark.skipif(
    shutil.which("svn") is None or shutil.which("svnadmin") is None,
    reason="SVN tools are not installed",
)


def run_svn(*args):
    subprocess.run(args, check=True, capture_output=True, text=True)


@pytest.fixture
def svn_project(tmp_path):
    """Create a small SVN repository with a nested KiCad project."""

    repo_path = tmp_path / "repo"
    working_copy = tmp_path / "wc"
    project_path = working_copy / "project"

    run_svn("svnadmin", "create", str(repo_path))
    run_svn("svn", "checkout", "--non-interactive", repo_path.as_uri(), str(working_copy))

    (project_path / "sub").mkdir(parents=True)
    (project_path / "top.kicad_sch").write_text("top schematic")
    (project_path / "board.kicad_pcb").write_text("board")
    # Subsheets can be anyway. We handle same dir, and sub dirs.
    (project_path / "sub-sheet.kicad_sch").write_text("sub schematic")
    (project_path / "sub" / "sub-dir-sheet.kicad_sch").write_text("nested schematic")
    (project_path / "sub" / "notes.txt").write_text("not a schematic")

    run_svn("svn", "add", "--non-interactive", str(project_path))
    run_svn("svn", "commit", "--non-interactive", str(working_copy), "-m", "first revision")

    (project_path / "sub" / "deep").mkdir()
    (project_path / "sub" / "deep" / "deep.kicad_sch").write_text("deep schematic")
    (project_path / "another.kicad_sch").write_text("another schematic")

    run_svn("svn", "add", "--non-interactive", str(project_path / "sub" / "deep"))
    run_svn("svn", "add", "--non-interactive", str(project_path / "another.kicad_sch"))
    run_svn("svn", "commit", "--non-interactive", str(working_copy), "-m", "second revision")
    run_svn("svn", "update", "--non-interactive", str(working_copy))

    return working_copy


def test_get_sch_files_with_and_without_revision(svn_project):
    """_get_sch_files should find every .kicad_sch file for either branch."""

    revision_one_files = scm._get_sch_files(str(svn_project), "project", "1")
    revision_two_files = scm._get_sch_files(str(svn_project), "project", "2")
    local_files = scm._get_sch_files(str(svn_project), "project")

    # Note order matters. Makes test more stringent, but harder to use. Probably not
    # more useful, on balance, but will do for now.
    assert revision_one_files == [
        "sub/sub-dir-sheet.kicad_sch",
        "sub-sheet.kicad_sch",
        "top.kicad_sch",
    ]
    assert revision_two_files == [
        "another.kicad_sch",
        "sub/deep/deep.kicad_sch",
        "sub/sub-dir-sheet.kicad_sch",
        "sub-sheet.kicad_sch",
        "top.kicad_sch",
    ]
    assert local_files == revision_two_files
