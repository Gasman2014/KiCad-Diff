#!/usr/bin/env python3

import wx
from kidiff_dialog import MyDialog

import os

class wxdialog(wx.Frame):

    def __init__(self, icon_path=None, repo_path=None, kicad_project_dir=None, board_filename=None, scm_name=None, scm_artifacts=None):
        super().__init__(parent=None, title='KiDiff - Select Commits for Comparison')
        dialog = MyDialog(self)

        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap(icon_path, wx.BITMAP_TYPE_ANY))
        dialog.SetIcon(_icon)

        dialog.main_group.StaticBox.SetLabel(scm_name + " Repository")
        if kicad_project_dir == ".":
            kicad_project_dir=""
        dialog.board_path.SetLabel(os.path.join(repo_path, kicad_project_dir, board_filename))

        for i, artifact in enumerate(scm_artifacts):
            dialog.commits_list_1.InsertItem(i, str(i))
            dialog.commits_list_1.SetItem(i, 1, artifact)
            dialog.commits_list_2.InsertItem(i, str(i))
            dialog.commits_list_2.SetItem(i, 1, artifact)

        dialog.commits_list_1.Focus(0)
        dialog.commits_list_2.Focus(1)
        dialog.commits_list_1.Select(0)
        dialog.commits_list_2.Select(1)

        res = dialog.ShowModal()

        if res == wx.ID_OK:
            selected_commit_1 = dialog.commits_list_1.GetFirstSelected()
            selected_commit_2 = dialog.commits_list_2.GetFirstSelected()
            self.commit1 = scm_artifacts[selected_commit_1]
            self.commit2 = scm_artifacts[selected_commit_2]

        if res == wx.ID_CANCEL:
            exit(1)

    def onClose(self, event):
        self.Close()


if __name__ == '__main__':
    app = wx.App(False)
    dialog = wxdialog("assets/favicon.ico", "repo_path/", ".", "board.kicad_pcb", "SCM", ["Commit 1", "Commit 2", "Commit 3"])
