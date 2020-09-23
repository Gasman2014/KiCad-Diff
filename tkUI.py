#!/usr/local/bin/python3

import subprocess
import tkinter as tk
from tkinter import *
from tkinter import filedialog, ttk, messagebox

global root, commitTop, commitBottom


import sys

def runProgram():
    # Just break out of mainloop to return current variables
    root.destroy()

def quit(self):
    root.destroy()


def CurSelect(event):
    global commitTop, commitBottom
    widget = event.widget
    selection = widget.curselection()
    picked = widget.get(selection)
    source = ((str(widget).split('.'))[1])[-1:]
    # TOP window is 3
    if source == '2':
        commitTop = picked
    # BOTTOM window is 4
    elif source == '3':
        commitBottom = picked


def runGUI(checkouts_top, prjctName, prjctPath, scm):

    global root
    global commitTop
    global commitBottom

    checkouts_bottom = checkouts_top[:]

    root = Tk()
    root.bind("<Escape>", quit)
    
    root.configure(background='#ececec')

    root.title("Kicad Visual Layout Diff")
    root.geometry('800x700')

    frame1 = tk.LabelFrame(root, text=scm, width=1000, height=50, bd=1, background='#ececec')
    frame2 = tk.LabelFrame(root, text="Commit 1", width=1000, height=200, bd=1, background='#ececec')
    frame3 = tk.LabelFrame(root, text="Commit 2", width=1000, height=200, bd=1, background='#ececec')
    frame4 = tk.LabelFrame(root, width=1000, height=50, bd=0, background='#ececec')

    frame1.grid(row=0, column=0, padx=25, sticky='N E W S')
    frame2.grid(row=1, column=0, padx=25, sticky='N E W')
    frame3.grid(row=2, column=0, padx=25, sticky='N EW')
    frame4.grid(row=3, column=0, padx=25, sticky='N E W S')

    root.grid_columnconfigure(0, weight=1)

    root.grid_rowconfigure(0, minsize=50,  weight=1)
    root.grid_rowconfigure(1, minsize=200, weight=2)
    root.grid_rowconfigure(2, minsize=200, weight=2)
    root.grid_rowconfigure(3, minsize=50,  weight=1)

    tk.Label(frame1, text=prjctPath, bg='#ececec').pack(side=LEFT, padx=10)
    tk.Label(frame1, text=prjctName, bg='#ececec').pack(side=LEFT, padx=10)

    commitTop = Variable()
    listTop = Listbox(
        frame2,
        bd=0,
        selectmode=SINGLE,
        exportselection=False,
        font='TkFixedFont')
    listTop.grid(column=0, row=0, sticky=(N, E, W))
    scrollTop = ttk.Scrollbar(frame2, orient=VERTICAL, command=listTop.yview)
    scrollTop.grid(column=1, row=0, sticky=(N, E, W))
    listTop['yscrollcommand'] = scrollTop.set

    listTop.bind('<<ListboxSelect>>', CurSelect)

    commitBottom = Variable()
    listBottom = Listbox(
        frame3,
        bd=0,
        selectmode=SINGLE,
        exportselection=False,
        font='TkFixedFont')
    listBottom.grid(column=0, row=0, sticky=(N, E, W))
    scrollBottom = ttk.Scrollbar(
        frame3, orient=VERTICAL, command=listBottom.yview)
    scrollBottom.grid(column=1, row=0, sticky=(N, E, W))
    listBottom['yscrollcommand'] = scrollBottom.set
    listBottom.bind('<<ListboxSelect>>', CurSelect)

    frame2.grid_columnconfigure(0, weight=1)
    frame2.grid_columnconfigure(1, weight=0)
    frame2.grid_rowconfigure(0, weight=1)

    frame3.grid_columnconfigure(0, weight=1)
    frame3.grid_columnconfigure(1, weight=0)
    frame3.grid_rowconfigure(0, weight=1)

    buttonOK = ttk.Button(frame4, text="OK", command=runProgram, default='active')
    buttonOK.grid(column=2, row=0, sticky='w', pady=10)

    buttonCancel = ttk.Button(frame4, text="Cancel", command=quit)
    buttonCancel.grid(column=1, row=0, sticky='e', pady=10)

    frame4.grid_columnconfigure(0, weight=0)
    frame4.grid_columnconfigure(1, weight=0)
    frame4.grid_columnconfigure(2, weight=10)

    for line in checkouts_top:
        listTop.insert(END, line)

    for i in range(1, len(checkouts_top), 2):
        listTop.itemconfigure(i, background='#ececec')

    for line in checkouts_bottom:
        # listBottom.insert(END, line[0:-1])
        listBottom.insert(END, line)

    for i in range(1, len(checkouts_bottom), 2):
        listBottom.itemconfigure(i, background='#ececec')

    for child in root.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.bind('<Return>', runProgram)

    root.update()
    root.mainloop()

    return(commitTop, commitBottom)
    root.destroy()
