#!/usr/bin/env python3

"""
Plot layers of kicad_pcb into .svg files
"""

import argparse
import os
import sys
import re
import shutil
import platform
import subprocess
import shlex

if platform.system() == "Darwin":
    sys.path.insert(0, "/Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/")
    sys.path.insert(0, "/Applications/KiCad/kicad.app/Contents/Frameworks/python/site-packages/")
    sys.path.insert(0, "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/")

import pcbnew as pn

pcbnew_version = pn.GetBuildVersion()
version_major = int(pcbnew_version.strip("()").split(".")[0])
version_minor = int(pcbnew_version.strip("()").split(".")[1])
version_patch = int(pcbnew_version.strip("()").split(".")[2].replace("-", "+").split("+")[0])
extra_version_str = pcbnew_version.replace("{}.{}.{}".format(version_major, version_minor, version_patch), "")


def processBoard(board_path, plot_dir, quiet=1, verbose=0, optimize_svg=0):
    """Load board and initialize plot controller"""

    if plot_dir != "./":
        shutil.copy(board_path, plot_dir)
        board_path = os.path.join(os.path.basename(board_path))
        print("> Changin path:", board_path)

    try:
        board = pn.LoadBoard(board_path)
    except:
        print("Wrong version of the API")
        print("Try sourcing 'env-nightly.sh' instead.")
        exit(1)

    board_version = board.GetFileFormatVersionAtLoad()
    print("\nBoard {}".format(board_version))

    boardbox = board.ComputeBoundingBox()
    boardxl = boardbox.GetX()
    boardyl = boardbox.GetY()
    boardwidth = boardbox.GetWidth()
    boardheight = boardbox.GetHeight()

    if verbose:
        print()
        print("    boardxl:", boardxl)
        print("    boardyl:", boardyl)
        print(" boardwidth:", boardwidth)
        print("boardheight:", boardheight)
        print()

    pctl = pn.PLOT_CONTROLLER(board)
    pctl.SetColorMode(True)

    # https://gitlab.com/kicad/code/kicad/-/blob/master/pcbnew/pcb_plot_params.h#L305
    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(plot_dir)

    popt.SetAutoScale(False)
    popt.SetUseAuxOrigin(False)
    popt.SetMirror(False)
    popt.SetUseGerberAttributes(True)
    popt.SetExcludeEdgeLayer(False)
    popt.SetSubtractMaskFromSilk(False)
    popt.SetPlotReference(True)
    popt.SetPlotValue(True)
    popt.SetPlotInvisibleText(True)

    # PcbNew >= 5.99
    if (version_major > 5) or ((version_major == 5) and (version_minor == 99)):
        print("Kicad v6")
        popt.SetPlotFrameRef(True)
        popt.SetWidthAdjust(pn.FromMM(0.15))
        popt.SetScale(1)

    # PcbNew < 5.99
    else:
        print("Kicad v5")
        popt.SetPlotFrameRef(False) # We want this True, but it breaks Kicad 5.1.*
        popt.SetLineWidth(pn.FromMM(0.15))
        popt.SetScale(2)

    # Board made with Kicad >= 5.99
    if board_version >= 20210000:
        if verbose:
            print("Board made with Kicad v6")

    # Board made with Kicad >= 5.99
    else:
        if verbose:
            print("Board made with Kicad v5")


    enabled_layers = board.GetEnabledLayers()
    layer_ids = list(enabled_layers.Seq())

    layer_names = []
    for layer_id in layer_ids:
        layer_names.append(board.GetLayerName(layer_id))
    max_string_len = max(layer_names, key=len)

    if optimize_svg:
        print("SVG optimization enabled")

    if not quiet:
        print("\n{} {} {} {}".format("#".rjust(2), "ID", "Name".ljust(len(max_string_len)), "Filename"))

    board_name = os.path.splitext(os.path.basename(board_path))[0]

    if plot_dir == "./":
        dirname = os.path.dirname(board_path)
    else:
        dirname = plot_dir

    for i, layer_id in enumerate(layer_ids):

        layer_name = board.GetLayerName(layer_id).replace(".", "_")
        filename_sufix = str(layer_id).zfill(2) + "-" + layer_name
        layer_filename = os.path.join(board_name + "-" + filename_sufix + ".svg")

        pctl.SetLayer(layer_id)
        svg_path = pctl.GetPlotFileName()

        if pctl.OpenPlotfile(filename_sufix, pn.PLOT_FORMAT_SVG, layer_name):
            pctl.PlotLayer()

        if optimize_svg:
            cmd = shlex.split("scour {0} --enable-viewboxing --enable-id-stripping --enable-comment-stripping --shorten-ids --indent=none".format(layer_filename))
            # cmd = shlex.split("svgo -i {0} --final-newline".format(layer_filename))
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

        if not quiet:
            print("{:2d} {:2d} {} {}".format(
                i + 1, layer_id,
                layer_name.ljust(len(max_string_len)),
                os.path.join(dirname, layer_filename)))


def list_layers(board_path):

    board = pn.LoadBoard(board_path)
    pctl = pn.PLOT_CONTROLLER(board)

    print("\n{} {} {}".format("#".rjust(2), "ID", "Name"))

    enabled_layers = board.GetEnabledLayers()
    layer_ids = list(enabled_layers.Seq())

    for i, layer_id in enumerate(layer_ids):
        layer_name = board.GetLayerName(layer_id)
        print("{:2d} {:2d} {}".format(i + 1, layer_id, layer_name))

    exit(0)


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Plot PCB Layers")
    parser.add_argument(
        "-o", "--output_folder", type=str, default="./", help="Output folder"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Run quietly")
    parser.add_argument(
        "-l", "--list", action="store_true", help="List used layers and exit"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Extra shows information"
    )
    parser.add_argument(
        "-x", "--optimize-svg", action="store_true", help="Optimize generated svg files"
    )
    parser.add_argument("kicad_pcb", nargs=1, help="Kicad PCB")
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = parse_cli_args()
    board_path = args.kicad_pcb[0]

    if not os.path.exists(board_path):
        print("Error: Board {} is missing".format(board_path))
        exit(1)

    if args.list:
        list_layers(board_path)

    if args.output_folder:
        plot_dir = args.output_folder
        if not os.path.exists(plot_dir):
            try:
                os.mkdir(plot_dir)
            except:
                print("Could not create", plot_dir)
                exit(1)

    if args.verbose:
        print()
        print("Kicad version:", pcbnew_version)
        print("Major version:", version_major)
        print("Minor version:", version_minor)
        print("Patch version:", version_patch)
        print("Extra version:", extra_version_str)

    processBoard(board_path, plot_dir, args.quiet, args.verbose, args.optimize_svg)
