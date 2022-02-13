#!/usr/bin/env python3
#
# A python script to select two revisions of a Kicad pcbnew layout
# held in a suitable version control repository and produce a graphical diff
# of generated svg files in a web browser.

import argparse
import os
import shutil
import re
import signal
import sys
import fnmatch

import wx
from kidiff_wxgui import wxdialog

import webbrowser
import http.server
import socketserver

import settings

import scms.fossil as fossil
import scms.git as git
import scms.svn as svn
import scms.generic as generic

import assets.html_data as custom_page


socketserver.TCPServer.allow_reuse_address = True
script_path = os.path.dirname(os.path.realpath(__file__))
assets_folder = os.path.join(script_path, "assets")
icon_path = os.path.join(assets_folder, "favicon.ico")

Handler = http.server.SimpleHTTPRequestHandler


def launch_filepicker():

    app = wx.App()

    frame = wx.Frame(None, -1, 'win.py')
    frame.SetSize(0,0,200,50)

    openFileDialog = wx.FileDialog(
        frame, "Open Kicad PCB", "", "",
        "Kicad PCB (*.kicad_pcb)|*.kicad_pcb",
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

    dialog = openFileDialog.ShowModal()

    if dialog == wx.ID_CANCEL:
        exit(1)

    kicad_board_path = openFileDialog.GetPath()
    repo_path, kicad_pcb = os.path.split(kicad_board_path)
    openFileDialog.Destroy()

    return (kicad_board_path, repo_path, kicad_pcb)


def launch_wxdialog(icon_path, repo_path, kicad_project_dir, board_filename, scm_name, scm_artifacts):
        app = wx.App(False)
        dialog = wxdialog(icon_path, repo_path, kicad_project_dir, board_filename, scm_name, scm_artifacts)
        return dialog.commit1, dialog.commit2


def get_project_scms(repo_path):
    """Determines which SCM is being used by the project.
    Current order of priority: Git > Fossil > SVN
    """

    scms = []

    if is_tool_available("git"):
        cmd = ["git", "status"]
        stdout, stderr = settings.run_cmd(repo_path, cmd)
        if (stdout != "") & (stderr == ""):
            scms.append("git")

    if is_tool_available("fossil"):
        cmd = ["fossil", "status"]
        stdout, stderr = settings.run_cmd(repo_path, cmd)
        if stdout != "":
            scms.append("fossil")

    if is_tool_available("svn"):
        cmd = [
            "svn",
            "log",
        ]  # | perl -l4svn log0pe "s/^-+/\n/"'.format(repo_path=repo_path)
        stdout, stderr = settings.run_cmd(repo_path, cmd)
        if (stdout != "") & (stderr == ""):
            scms.append("svn")

    return scms


def make_svg(kicad_pcb_path, repo_path, kicad_project_dir, board_filename, commit1, commit2, plot_page_frame):
    """Hands off required .kicad_pcb files to "plotpcb"
    and generate .svg files. Routine is quick so all
    layers are plotted to svg."""

    commit1_hash = "local"
    commit2_hash = "local"

    if not commit1 == board_filename:
        commit1_hash = commit1[:7]

    if not commit2 == board_filename:
        commit2_hash = commit2[:7]

    # Output folder
    commit1_output_path = os.path.join(settings.output_dir, commit1_hash)
    commit2_output_path = os.path.join(settings.output_dir, commit2_hash)

    if not os.path.exists(commit1_output_path):
        os.makedirs(commit1_output_path)

    if not os.path.exists(commit2_output_path):
        os.makedirs(commit2_output_path)

    plot1_cmd = [settings.plot_prog, board_filename]
    plot2_cmd = [settings.plot_prog, board_filename]

    if plot_page_frame:
        print("\nPlotting the page with frame")
        plot1_cmd.append("-f")
        plot2_cmd.append("-f")

    stdout, stderr = settings.run_cmd(commit1_output_path, plot1_cmd)
    plot1_stdout = stdout.splitlines()
    plot1_stderr = stderr

    if plot1_stderr != "":
        print(plot1_stdout)
        print(plot1_stderr)

    stdout, stderr = settings.run_cmd(commit2_output_path, plot2_cmd)
    plot2_stdout = stdout.splitlines()
    plot2_stderr = stderr

    if plot2_stderr != "":
        print(plot1_stdout)
        print(plot1_stderr)

    if not plot1_stdout or not plot2_stdout:
        print("ERROR: Something happened with plotpcb")
        exit(1)

    return commit1_hash, commit2_hash



def generate_assets(repo_path, kicad_project_dir, board_filename, output_dir1, output_dir2):
    """
    Setup web directories for output
    """

    web_dir = os.path.join(settings.output_dir, settings.web_dir)
    triptych_dir = os.path.join(settings.output_dir, settings.web_dir + "/triptych/")

    web_index = os.path.join(web_dir + "/index.html")
    web_style = os.path.join(web_dir + "/style.css")
    triptych_style = os.path.join(triptych_dir + "triptych.css")
    web_favicon = os.path.join(web_dir + "/favicon.ico")
    blank_svg = os.path.join(assets_folder + "/blank.svg")

    if not os.path.exists(web_dir):
        os.makedirs(web_dir)
        os.makedirs(os.path.join(web_dir, "triptych"))

    mainpage_css = os.path.join(assets_folder, "style.css")
    shutil.copyfile(mainpage_css, web_style)

    triptych_css = os.path.join(assets_folder, "triptych.css")
    shutil.copyfile(triptych_css, triptych_style)

    favicon = os.path.join(assets_folder, "favicon.ico")
    shutil.copyfile(favicon, web_favicon)

    if os.path.exists(web_index):
        os.remove(web_index)

    source_dir1 = os.path.join(settings.output_dir, output_dir1)
    source_dir2 = os.path.join(settings.output_dir, output_dir2)

    project_name, _ = os.path.splitext(board_filename)
    svg_files1 = sorted(fnmatch.filter(os.listdir(source_dir1), project_name + '-[0-9][0-9]-*.svg'))
    svg_files2 = sorted(fnmatch.filter(os.listdir(source_dir2), project_name + '-[0-9][0-9]-*.svg'))
    layers = dict()

    for i, f in enumerate(svg_files1):
        file_name, _ = os.path.splitext(os.fsdecode(f))
        project_name, _ = os.path.splitext(board_filename)
        layer_id = int(file_name.replace(project_name + "-", "")[0:2])
        layer_name = file_name.replace(project_name + "-", "")[3:]
        layers[layer_id] = (file_name, None)

    for i, f in enumerate(svg_files2):
        file_name, _ = os.path.splitext(os.fsdecode(f))
        project_name, _ = os.path.splitext(board_filename)
        layer_id = int(file_name.replace(project_name + "-", "")[0:2])
        layer_name = file_name.replace(project_name + "-", "")[3:]
        if layers[layer_id]:
            layer = layers[layer_id]
            layers[layer_id] = (layer[0], file_name)
        else:
            layers[layer_id] = (None, file_name)

    for i in sorted(layers.keys()):
        if layers[i][0] == None:
            missing_svg = os.path.join(source_dir1, layers[i][1] + ".svg")
            print("Creating blank", missing_svg)
            shutil.copyfile(blank_svg, missing_svg)

        if layers[i][1] == None:
            missing_svg = os.path.join(source_dir2, layers[i][0] + ".svg")
            shutil.copyfile(blank_svg, missing_svg)
            print("Creating blank", missing_svg)

    return


def getBoardData(board):
    """Takes a board reference and returns the
    basic parameters from it.
    Might be safer to split off the top section
    before the modules to avoid the possibility of
    recycling keywords like 'title'"""

    prms = {
        "title": "",
        "rev": "",
        "company": "",
        "date": "",
        "page": "",
        "thickness": 0,
        "drawings": 0,
        "tracks": 0,
        "zones": 0,
        "modules": 0,
        "nets": 0,
    }

    with open(board, "r") as f:
        for line in f:
            words = line.strip("\t ()").split()
            for key in prms:
                if len(words) > 1:
                    if key == words[0]:
                        complete = ""
                        for i in range(1, len(words)):
                            complete += words[i].strip("\t ()").replace('"', "") + " "
                        prms[key] = complete
    return prms


def html_class_from_layer_id(layer_id):
    # KEEP THIS LIST ORDERED
    # Use this to select the right class (color) on css
    # https://docs.kicad.org/doxygen/layers__id__colors__and__visibility_8h_source.html

    # Cycle layer colors in inner layers
    if (layer_id >= 8) and (layer_id <= 30):
        layer_id = layer_id % 8

    layer_name = [
        "F_Cu",
        "In1_Cu",
        "In2_Cu",
        "In3_Cu",
        "In4_Cu",
        "In5_Cu",
        "In6_Cu",
        "In7_Cu",
        "In8_Cu",
        "In9_Cu",
        "In10_Cu",
        "In11_Cu",
        "In12_Cu",
        "In13_Cu",
        "In14_Cu",
        "In15_Cu",
        "In16_Cu",
        "In17_Cu",
        "In18_Cu",
        "In19_Cu",
        "In20_Cu",
        "In21_Cu",
        "In22_Cu",
        "In23_Cu",
        "In24_Cu",
        "In25_Cu",
        "In26_Cu",
        "In27_Cu",
        "In28_Cu",
        "In29_Cu",
        "In30_Cu",
        "B_Cu",  # 31
        "B_Adhes",
        "F_Adhes",
        "B_Paste",
        "F_Paste",
        "B_SilkS",
        "F_SilkS",
        "B_Mask",
        "F_Mask",  # 39
        "Dwgs_User",
        "Cmts_User",
        "Eco1_User",
        "Eco2_User",
        "Edge_Cuts",
        "Margin",
        "B_CrtYd",
        "F_CrtYd",
        "B_Fab",
        "F_Fab",  # 49
        "User_1",
        "User_2",
        "User_3",
        "User_4",
        "User_5",
        "User_6",
        "User_7",
        "User_8",
        "User_9",
        "Rescue",  # 59
    ]

    # Reuse some colors
    if (layer_id >= 50):
        class_name = "User"
    else:
        class_name = layer_name[layer_id]

    return class_name


def assemble_html(kicad_pcb_path, repo_path, kicad_project_dir, board_filename, output_dir1, output_dir2, commit_datetimes):
    """Write out HTML using template. Iterate through files in diff directories, generating
    thumbnails and three way view (triptych) page.
    """

    web_dir = os.path.join(settings.output_dir, settings.web_dir)
    web_index = os.path.join(web_dir, "index.html")

    board1_path = os.path.join(settings.output_dir, output_dir1, board_filename)
    board2_path = os.path.join(settings.output_dir, output_dir2, board_filename)

    index_html = open(web_index, "w")

    date1, time1, date2, time2 = commit_datetimes.replace('"', "").split(" ")

    board1_info = getBoardData(board1_path)
    board2_info = getBoardData(board2_path)

    board_title = board1_info.get("title")
    board_company = board1_info.get("company")

    # ======

    thickness1 = board1_info.get("thickness")
    drawings1 = board1_info.get("drawings")
    tracks1 = board1_info.get("tracks")
    zones1 = board1_info.get("zones")
    modules1 = board1_info.get("modules")
    nets1 = board1_info.get("nets")

    # ======

    thickness2 = board2_info.get("thickness")
    drawings2 = board2_info.get("drawings")
    tracks2 = board2_info.get("tracks")
    zones2 = board2_info.get("zones")
    modules2 = board2_info.get("modules")
    nets2 = board2_info.get("nets")

    index_header = custom_page.index_header.format(
        board_title=board_title,
        board_company=board_company,
        date1=date1,
        date2=date2,
        time1=time1,
        time2=time2,
        hash1=output_dir1,
        hash2=output_dir2,
        thickness1=thickness1,
        thickness2=thickness2,
        drawings1=drawings1,
        drawings2=drawings2,
        tracks1=tracks1,
        tracks2=tracks2,
        zones1=zones1,
        zones2=zones2,
        modules1=modules1,
        modules2=modules2,
        nets1=nets1,
        nets2=nets2,
    )

    index_html.write(index_header)

    source_dir = os.path.join(settings.output_dir, output_dir1)
    triptych_dir = os.path.join(settings.output_dir, "web", "triptych")

    if not os.path.exists(triptych_dir):
        os.makedirs(triptych_dir)

    board1_path = os.path.join(output_dir1, board_filename)
    board2_path = os.path.join(output_dir2, board_filename)
    diff_path   = os.path.join(settings.output_dir, "diff.txt")

    stdout, stderr = settings.run_cmd(settings.output_dir, [settings.diffProg, board2_path, board1_path])

    with open(diff_path, "a") as fout:
        fout.write(stdout)

    project_name, _ = os.path.splitext(board_filename)
    svg_files = sorted(fnmatch.filter(os.listdir(source_dir), project_name + '-[0-9][0-9]-*.svg'))
    triptych_htmls = [svg_file.replace('.svg', '.html') for svg_file in svg_files]

    for i, f in enumerate(svg_files):

        file_name, _ = os.path.splitext(os.fsdecode(f))
        layer_id = int(file_name.replace(project_name + "-", "")[0:2])
        layer_name = file_name.replace(project_name + "-", "")[3:]
        layer_name_orig = layer_name.replace("_", ".")  # not sure this is good and works all the time

        triptych_html = file_name + ".html"
        triptych_html_path = os.path.join(triptych_dir, triptych_html)

        index_gallery_item = custom_page.index_gallery_item.format(
            hash1=output_dir1,
            hash2=output_dir2,
            layer_name=layer_name,
            filename_svg=f,
            triptych_html=triptych_html,
            layer_class=html_class_from_layer_id(layer_id),
            index=i+1,
        )

        index_html.write(index_gallery_item)

        with open(triptych_html_path, "w") as triptych_out_html:

            if i+1 >= len(triptych_htmls):
                n = 0
            else:
                n = i+1

            triptych_data = custom_page.triptych_html.format(
                hash1=output_dir1,
                hash2=output_dir2,
                layer_name=layer_name,
                filename_svg=f,
                layer_class=html_class_from_layer_id(layer_id),
                previous_page=triptych_htmls[i-1],
                next_page=triptych_htmls[n],
                index=i+1,
                homepage="../../../web/",
                board_title=board_title,
            )

            triptych_out_html.write(triptych_data)

            out_html = "\n".join(
                re.sub("status [1-9][0-9]", "", line)
                for line in stdout.splitlines()
                if layer_name_orig in line
            )

            processed = process_diff(out_html, layer_name_orig)
            processed += custom_page.triptych_footer

            triptych_out_html.write(processed)

    index_html.write(custom_page.index_footer)


def process_diff(diff_text, mod):

    keywords = [
        ("module ", "Modules", ("Component", "Reference", "Timestamp")),
        ("gr_text ", "Text", ("Text", "Position")),
        ("\\(via ", "Vias", ("Coordinate", "Size", "Drill", "Layers", "Net")),
        ("fp_text \\w+ ", "FP Text", ("Reference", "Coordinate")),
        (
            "\\(pad ",
            "Pads",
            ("Number", "Type", "Shape", "Coordinate", "Size", "Layers", "Ratio"),
        ),
        ("\\(gr_line ", "Graphics", ("Start", "End ", "Width", "Net")),
        ("\\(fp_arc", "Arcs", ("Start", "End ", "Angle", "Width")),
        ("\\(segment", "Segments", ("Start", "End ", "Width", "Net", "Timestamp")),
        ("\\(fp_circle", "Circles", ("Centre", "End ", "Width")),
    ]

    d = {
        "\\(start ": "<td>",
        "\\(end ": "<td>",
        "\\(width ": "<td>",
        "\\(tedit ": "<td>",
        "\\(tstamp ": "<td>",
        "\\(at ": "<td>",
        "\\(size ": "<td>",
        "\\(drill ": "<td>",
        "\\(layers ": "<td>",
        "\\(net ": "<td>",
        "\\(roundrect_rratio ": "<td>",
        "\\(angle ": "<td>",
        "\\(center ": "<td>",
        "\\)": "</td>",
        "user (\\w+)": r"<td>\1</td>",
        "reference (\\w+)": r"<td>\1</td>",
        "([0-9]) smd": r"<td>\1</td><td>Surface</td>",
        "roundrect": "<td>Rounded</td>",
        "rect": "<td>Rectangle</td>",
        "\\(([^ ]+) ": r"<td>\1</td>",
        '(?<=")(.*)(?=")': r"<td>\1</td>",
        '["]': r"",
        "[**]": r"",
    }

    final = ""
    content = ""
    output = ""
    combined = ""
    tbL = ""
    tbR = ""
    checked = "checked='checked'"

    top1 = """
        <input name='tabbed' id='tabbed{tabn}' type='radio' {checked}/>
        <section>
            <h1>
                <label for='tabbed{tabn}'>{label}</label>
            </h1>
            <div>
                {content}
            </div>
        </section>
    """

    tsl = """
        <div class='responsive'>
            <div class = 'tbl'>
                <table style="border: 2px solid #555; width: 100%; height: 2px;">
    """

    tsr = """
        <div class='responsive'>
            <div class = 'tbr'>
                <table style="border: 2px solid #555; width: 100%; height: 2px;">
    """

    clearfix = """
        <div class='clearfix'></div>
        <div style='padding:6px;'></div>
    """

    for indx, layer_info in enumerate(keywords):

        combined = tbL = tbR = "<tr>"
        for indx2, parameter in enumerate(layer_info[2]):
            tbR = tbR + "<th>" + parameter + "</th>\n"
            tbL = tbL + "<th>" + parameter + "</th>\n"
        tbR = tbR + "</tr>"
        tbL = tbL + "</tr>"

        for line in diff_text.splitlines():
            if re.search(layer_info[0], line) and (mod in line):
                output = re.sub(layer_info[0], "", line)
                output = output.replace("(layer " + mod + ")", "")

                for item, replace in d.items():
                    output = re.sub(item, replace, output)

                if output.count("<td>") == indx2:
                    output += "<td></td>\n"

                if output == "<td>":
                    output = ""

                output += "</tr>\n"

                if output[0] == ">":
                    tbL = tbL + "<tr>" + output[1:]
                elif output[0] == "<":
                    tbR = tbR + "<tr>" + output[1:]

        combined = (
            tsl + tbL + "</table></div></div>\n" + tsr + tbR + "</table></div></div>\n"
        )

        content = top1.format(
            tabn=indx, content=combined, label=layer_info[1], checked=checked
        )

        checked = ""

        final = final + content

    final = "<div class = 'tabbed'>" + final + "</div>" + clearfix

    return final


def is_tool_available(name):
    from shutil import which

    return 1 if which(name) is not None else 0


class WebServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            directory=os.path.realpath(os.path.join(settings.output_dir)),
            **kwargs
        )

    def log_message(self, format, *args):
        return


# class Select(Toplevel):
#     def __init__(self, parent=None):
#         Toplevel.__init__(self, parent)
#         # self.wm_title("Settings")
#         Toplevel.withdraw(self)
#         Toplevel.update(self)
#             message="Select the board file (*.kicad_pcb) file under version control",
#             detail="Available: \n\n" + scm,
#         )
#         self.update()

#         if action == "cancel":
#             self.quit()


def start_web_server(port, kicad_project_path):
    with socketserver.TCPServer(("", port), WebServerHandler) as httpd:
        url = "http://127.0.0.1:{port}/web/index.html".format(port=str(port))
        print("")
        print("Starting webserver at {url}".format(url=url))
        print("(Hit Ctrl+C to exit)")
        webbrowser.open(url)
        httpd.serve_forever()


def signal_handler(sig, frame):
    sys.exit(0)


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Kicad PCB visual diffs.")
    parser.add_argument("-a", "--commit1-hash", type=str, help="Commit 1 hash")
    parser.add_argument("-b", "--commit2-hash", type=str, help="Commit 2 hash")
    parser.add_argument("-g", "--gui", action="store_true", help="Use gui")
    parser.add_argument("-s", "--scm", type=str, help="Select SCM (git, svn, fossil)")
    parser.add_argument(
        "-d",
        "--display",
        type=str,
        help="Set DISPLAY value, default :1.0",
        default=":1.0",
    )
    parser.add_argument(
        "-p", "--port", type=int, help="Set webserver port", default=9092
    )
    parser.add_argument(
        "-w",
        "--webserver-disable",
        action="store_true",
        help="Does not execute webserver (just generate images)",
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity (-vvv)"
    )
    parser.add_argument(
        "kicad_pcb", metavar="PCB_PATH", nargs="?", help="Kicad PCB path"
    )
    parser.add_argument(
        "-o", "--output-dir", type=str, default=".kidiff", help="Set output directory. Default is '.kidiff'.")
    parser.add_argument(
        "-l", "--list-commits", action="store_true", help="List commits and exit"
    )
    parser.add_argument(
        "-f", "--frame", action="store_true", help="Plot whole page frame"
    )

    args = parser.parse_args()

    if args.verbose >= 3:
        print("")
        print("Command Line Arguments")
        print(args)

    return args


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    args = parse_cli_args()

    if args.verbose:
        settings.verbose = args.verbose

    if args.kicad_pcb is None:
        kicad_pcb_path, kicad_project_path, board_filename = launch_filepicker()
    else:
        kicad_pcb_path = os.path.realpath(args.kicad_pcb)
        kicad_project_path = os.path.dirname(kicad_pcb_path)
        board_filename = os.path.basename(os.path.realpath(args.kicad_pcb))

        if not os.path.exists(args.kicad_pcb):
            print("Kicad file {} does not exit".format(args.kicad_pcb))
            exit(1)

        _, extension = os.path.splitext(args.kicad_pcb)
        if extension != ".kicad_pcb":
            print("The file {} seems not to be a Kicad PCB".format(args.kicad_pcb))
            exit(1)

    project_scms = get_project_scms(kicad_project_path)

    if args.scm:
        scm_name = args.scm.lower()
    else:
        scm_name = project_scms[0]
    scm = generic.scm()
    if scm_name == "fossil":
        scm = fossil.scm()
    elif scm_name == "svn":
        scm = svn.scm()
    elif scm_name == "git":
        scm = git.scm()
    else:
        print(
            "This project is either not under version control"
            "or no SCM tool was was found in the PATH"
        )
        sys.exit(1)

    repo_path, kicad_project_dir = scm.split_repo_path(kicad_project_path)

    avaialble_scms = (
        ""
        if len(project_scms) <= 1
        else "(available: {})".format(", ".join(map(str, project_scms)))
    )

    if args.output_dir == ".kidiff":
        kicad_pcb_dir = os.path.dirname(kicad_pcb_path)
        settings.output_dir = os.path.join(kicad_pcb_dir, args.output_dir)
    else:
        settings.output_dir = os.path.realpath(args.output_dir)

    print("")
    print("      SCM Selected:", scm_name, avaialble_scms)
    print("  Kicad Board Path:", kicad_pcb_path)
    print("Kicad Project Path:", kicad_project_path)
    print("         REPO Path:", repo_path)
    print(" Kicad Project Dir:", kicad_project_dir)
    print("   Board File Name:", board_filename)
    print("        Output Dir:", settings.output_dir)

    scm_artifacts = scm.get_artefacts(repo_path, kicad_project_dir, board_filename)

    if args.verbose >= 1 or args.list_commits:
        print("")
        print("COMMITS LIST")
        for artifact in scm_artifacts:
            if artifact != " ":
                print(artifact)

    if args.list_commits:
        exit(1)

    if args.commit1_hash is None or args.commit2_hash is None:
        commit1, commit2 = launch_wxdialog(icon_path, repo_path, kicad_project_dir, board_filename, scm_name, scm_artifacts)

        if not commit1 or not commit2:
            print("\nERROR: You must select both commits.")
            exit(1)

    if args.commit1_hash is not None:
        commit1 = args.commit1_hash

    if args.commit2_hash is not None:
        commit2 = args.commit2_hash

    print("")
    print("Commit 1 (a):", commit1)
    print("Commit 2 (b):", commit2)

    commit1, commit2, commit_datetimes = scm.get_boards(kicad_pcb_path, repo_path, kicad_project_dir, board_filename, commit1, commit2)

    output_dir1, output_dir2 = make_svg(kicad_pcb_path, repo_path, kicad_project_dir, board_filename, commit1, commit2, args.frame)

    generate_assets(repo_path, kicad_project_dir, board_filename, output_dir1, output_dir2)

    assemble_html(kicad_pcb_path, repo_path, kicad_project_dir, board_filename, output_dir1, output_dir2, commit_datetimes)

    if not args.webserver_disable:
        try:
            start_web_server(args.port, kicad_project_dir)
        except:
            print("\nPort {} already in use.".format(args.port))
            print("Kill previews server or change the port with '-p PORT_NUMBER'")