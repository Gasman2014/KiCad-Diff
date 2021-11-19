#!/usr/bin/env python3

"""
Plot layers of kicad_pcb into .svg files
"""

import argparse
import os
import sys
import re

import platform

if platform.system() == "Darwin":
    sys.path.insert(
        0, "/Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/"
    )

import pcbnew as pn

pcbnew_version = pn.GetBuildVersion()
version_major = int(pcbnew_version.strip("()").split(".")[0])
version_minor = int(pcbnew_version.strip("()").split(".")[1])
version_patch = int(pcbnew_version.strip("()").split(".")[2].replace("-", "+").split("+")[0])
extra_version_str = pcbnew_version.replace("{}.{}.{}".format(version_major, version_minor, version_patch), "")


def processBoard(board_path, plot_dir, quiet=0, verbose=0):
    """Load board and initialize plot controller"""

    try:
        board = pn.LoadBoard(board_path)
    except:
        print("Wrong version of the API")
        print("Try sourcing 'env-nightly.sh' instead.")
        exit(1)

    board_version = board.GetFileFormatVersionAtLoad()
    print("\nBoard version: {}".format(board_version))

    board_name = os.path.basename(board_path)

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

    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(plot_dir)
    popt.SetPlotFrameRef(False)

    if (version_major > 5) or (version_major == 5) and (version_minor == 99):
        popt.SetWidthAdjust(pn.FromMM(0.15))
    else:
        popt.SetLineWidth(pn.FromMM(0.15))

    popt.SetAutoScale(False)

    if board_version >= 20210000:
        if verbose:
            print("Using nightly build")
        popt.SetScale(1)
    else:
        if verbose:
            print("Using current settings")
        popt.SetScale(2)

    popt.SetMirror(False)
    popt.SetUseGerberAttributes(True)
    popt.SetExcludeEdgeLayer(False)
    popt.SetUseAuxOrigin(True)

    enabled_layers = board.GetEnabledLayers()
    layer_ids = list(enabled_layers.Seq())

    layer_names = []
    for layer_id in layer_ids:
        layer_names.append(board.GetLayerName(layer_id))
    max_string_len = max(layer_names, key=len)

    if not quiet:
        print("\n{} {} {} {}".format("#".rjust(2), "ID", "Name".ljust(len(max_string_len)), "Filename"))

    for i, layer_id in enumerate(layer_ids):

        pctl.SetLayer(layer_id)

        layer_name = board.GetLayerName(layer_id).replace(".", "_")
        plot_sufix = str(layer_id).zfill(2) + "-" + layer_name
        layer_filename = os.path.join(board_path + "-" + plot_sufix + ".svg")

        pctl.OpenPlotfile(plot_sufix, pn.PLOT_FORMAT_SVG, layer_name)
        pctl.PlotLayer()

        if not quiet:
            print("{:2d} {:2d} {} {}".format(
                i + 1, layer_id, layer_name.ljust(len(max_string_len)), layer_filename
                )
            )


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


    print("board_path:", board_path)
    print("plot_dir:", plot_dir)

    if args.verbose:
        print()
        print("Kicad version:", pcbnew_version)
        print("Major version:", version_major)
        print("Minor version:", version_minor)
        print("Patch version:", version_patch)
        print("Extra version:", extra_version_str)

    processBoard(board_path, plot_dir, args.quiet, args.verbose)
