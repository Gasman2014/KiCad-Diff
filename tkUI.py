#!/usr/local/bin/python3

from tkinter import ttk, Tk, LabelFrame, Label, Variable, IntVar, Listbox, \
    SINGLE, N, E, W, VERTICAL, LEFT, END, CENTER, Radiobutton

global root, commitTop, commitBottom


def runProgram():
    root.destroy()


def quit(self):
    root.destroy()
    exit(0)


def cancel():
    root.destroy()
    exit(0)


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


def select_scm_gui():

    global root

    root = Tk()
    root.title("SCM")

    root.bind("<Escape>", quit)
    root.protocol('WM_DELETE_WINDOW', cancel)

    v = IntVar()
    v.set(-1)

    scms = [
        ("Fossil"),
        ("Git"),
        ("SVN"),
    ]

    def ShowChoice():
        root.destroy()

    Label(root, text="""Select the project's SCM""", justify=CENTER, padx=20).pack()

    for val, language in enumerate(scms):
        Radiobutton(
            root,
            text=language,
            indicatoron=0,
            width=20,
            padx=20,
            variable=v,
            command=ShowChoice,
            value=val).pack(anchor=W)

    root.mainloop()

    try:
        scm = v.get()
    except Exception:
        scm = v
    return scms[scm]


def runGUI(checkouts_top, prjctName, kicad_project_path, prjctPath, scm):

    global root
    global commitTop
    global commitBottom

    checkouts_bottom = checkouts_top[:]

    root = Tk()
    root.bind("<Escape>", quit)

    root.configure(background='#ececec')

    root.title("Kicad Visual Layout Diff")
    root.geometry('800x700')

    frame1 = LabelFrame(root, text=scm.upper(), width=1000, height=25, bd=1, background='#ececec', foreground='#000000')
    frame2 = LabelFrame(root, text="Commit 1 (a)", width=1000, height=200, bd=1, background='#ececec', foreground='#000000')
    frame3 = LabelFrame(root, text="Commit 2 (b)", width=1000, height=200, bd=1, background='#ececec', foreground='#000000')
    frame4 = LabelFrame(root, width=1000, height=10, bd=0, background='#ececec', foreground='#000000')

    frame1.grid(row=0, column=0, padx=25, sticky='N E W S')
    frame2.grid(row=1, column=0, padx=25, sticky='N E W')
    frame3.grid(row=2, column=0, padx=25, sticky='N E W')
    frame4.grid(row=3, column=0, padx=25, sticky='N E W S')

    root.grid_columnconfigure(0, weight=1)

    root.grid_rowconfigure(0, minsize=25,  weight=2)
    root.grid_rowconfigure(1, minsize=200, weight=4)
    root.grid_rowconfigure(2, minsize=200, weight=4)
    root.grid_rowconfigure(3, minsize=10,  weight=1)

    if kicad_project_path == '.':
        pcb_path = prjctPath + "/" + prjctName
    else:
        pcb_path = prjctPath + "/" + kicad_project_path + "/" + prjctName

    pcb_path = pcb_path.replace("//", "/")

    Label(frame1, text=pcb_path, bg='#ececec', fg='#000000').pack(side=LEFT, padx=10)

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

    buttonCancel = ttk.Button(frame4, text="Cancel", command=cancel)
    buttonCancel.grid(column=1, row=0, sticky='e', pady=10)

    frame4.grid_columnconfigure(0, weight=0)
    frame4.grid_columnconfigure(1, weight=0)
    frame4.grid_columnconfigure(2, weight=10)

    for line in checkouts_top:
        listTop.insert(END, line)

    for i in range(1, len(checkouts_top), 2):
        listTop.itemconfigure(i, background='#ececec', foreground='#000000')

    for line in checkouts_bottom:
        # listBottom.insert(END, line[0:-1])
        listBottom.insert(END, line)

    for i in range(1, len(checkouts_bottom), 2):
        listBottom.itemconfigure(i, background='#ececec', foreground='#000000')

    for child in root.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.bind('<Return>', runProgram)

    root.update()
    root.mainloop()

    try:
        commitTop_str = commitTop.get()
    except:
        commitTop_str = commitTop

    try:
        commitBottom_str = commitBottom.get()
    except:
        commitBottom_str = commitBottom

    return(commitTop_str.strip("\""), commitBottom_str.strip("\""))
    root.destroy()
