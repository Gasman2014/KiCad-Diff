#!/usr/local/bin/python3

import os
import pygubu

from tkinter import (
    ttk,
    Tk,
    LabelFrame,
    Label,
    Variable,
    IntVar,
    Listbox,
    SINGLE,
    N,
    END,
    W,
    VERTICAL,
    LEFT,
    END,
    CENTER,
    Radiobutton,
)


PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "kidiff.ui")


class KidiffApp:
    def __init__(self, repo_path, kicad_project_dir, board_filename, scm, scm_artifacts):

        self.scm_artifacts = scm_artifacts
        self.board_filename = board_filename
        self.kicad_project_dir = kicad_project_dir
        self.repo_path = repo_path
        self.scm = scm

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.main_window = builder.get_object("main_window")
        builder.connect_callbacks(self)

        self.main_window.bind("<Escape>", self.on_escape_key)
        self.main_window.bind("<Return>", self.get_selected_commits)

        self.set_repo_info()
        self.set_repo_path()
        self.fill_scm_artifacts()

        self.commit1 = ""
        self.commit2 = ""

    def on_escape_key(self, event=None):
        self.on_cancel_button_click(self)

    def on_cancel_button_click(self, event=None):
        self.main_window.destroy()
        exit(0)

    def get_selected_commits(self, event=None):

        try:
            self.commit1_str = self.commit1.get()
        except:
            self.commit1_str = self.commit1

        try:
            self.commit2_str = self.commit2.get()
        except:
            self.commit2_str = self.commit2

        self.main_window.destroy()

    def callback(self, event=None):
        pass

    def set_repo_info(self):
        scm_info = "{} Repository".format(self.scm.upper())
        self.labelframe_1 = self.builder.get_object("labelframe_1")
        self.labelframe_1["text"] = scm_info

    def set_repo_path(self):

        if self.kicad_project_dir == ".":
            board_path = os.path.join(self.repo_path, self.board_filename)
        else:
            board_path = (
                os.path.join(self.repo_path, self.kicad_project_dir, self.board_filename)
            )

        self.board_path = self.builder.get_object("board_path")
        self.board_path["text"] = board_path

    def get_text_from_select_rows(self, event=None):
        self.commit1 = self.listbox_1.get(self.listbox_1.curselection())
        self.commit2 = self.listbox_2.get(self.listbox_2.curselection())

    def update_commit1(self, event):
        self.commit1 = self.listbox_1.get(self.listbox_1.curselection())

    def update_commit2(self, event):
        self.commit2 = self.listbox_2.get(self.listbox_2.curselection())

    def fill_scm_artifacts(self):

        self.listbox_1 = self.builder.get_object("listbox_1")
        self.listbox_2 = self.builder.get_object("listbox_2")

        self.listbox_1.bind("<<ListboxSelect>>", self.update_commit1)
        self.listbox_2.bind("<<ListboxSelect>>", self.update_commit2)

        # Fill scm_artifacts
        for i, line in enumerate(self.scm_artifacts):
            self.listbox_1.insert(END, line)
            self.listbox_2.insert(END, line)

            # Alternate row colors
            if i % 2:
                self.listbox_1.itemconfigure(
                    i, background="#ececec", foreground="#000000"
                )
                self.listbox_2.itemconfigure(
                    i, background="#ececec", foreground="#000000"
                )

        # Commit set on first commit by default
        if len(self.scm_artifacts) >= 1:

            self.listbox_1.select_set(0)  # This only sets focus
            self.listbox_1.event_generate("<<ListboxSelect>>")
            self.commit1 = self.listbox_1.get(self.listbox_1.curselection())

            # Commit set on the second commit by default
            if len(self.scm_artifacts) >= 2:
                self.listbox_2.select_set(1)  # This only sets focus
                self.listbox_2.event_generate("<<ListboxSelect>>")
                self.commit2 = self.listbox_2.get(self.listbox_2.curselection())
            else:
                self.listbox_2.select_set(0)  # This only sets focus
                self.listbox_2.event_generate("<<ListboxSelect>>")
                self.commit2 = self.listbox_2.get(self.listbox_2.curselection())

    def run(self):

        self.get_text_from_select_rows()

        # self.main_window.update()
        self.main_window.mainloop()


def runGUI(repo_path, kicad_project_dir, board_filename, scm, scm_artifacts):

    app = KidiffApp(repo_path, kicad_project_dir, board_filename, scm, scm_artifacts)
    app.run()
    return app.commit1, app.commit2
