#!/usr/bin/env python3
"""Word Search Generator app main

The app face of the program, both CLI and GUI.

This file is part of Word Search Generator.

Word Search Generator is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.

S.D.G."""


import argparse
import sys
from warnings import warn

try:
    from . import qt_mainwindow
    HAVE_QT = True
except ImportError as e:
    warn(f"Could not import the Qt GUI module: {e}")
    HAVE_QT = False

from . import tk_mainwindow

from .algorithm import (
    Generator,
    ALL_CHARS,
    DIRECTIONS,
    EASY_DIRECTIONS,
    SIZE_FAC_DEFAULT,
    INTERSECT_BIAS_NAMES,
    INTERSECT_BIAS_DEFAULT,
    )


def main() -> int:
    """
    The app main function

    Returns:
        Status (int): The exit status of the program.
    """
    parser = argparse.ArgumentParser(
        prog="wordsearchgen",
        description="Generate word search puzzles, CLI or GUI. CLI mode is " +
        "triggered by passing any words to the command.",
        epilog="S.D.G.",
        )

    parser.add_argument(
        "-t", "--use-tk",
        action="store_true",
        help="(GUI) Use the legacy Tk GUI instead of Qt",
        )
    parser.add_argument(
        "-H", "--use-hard",
        action="store_true",
        help="Use the harder, backwards (11-o'-clock) directions",
        )
    parser.add_argument(
        "-s", "--size-factor",
        type=int,
        help="Set the starting factor of how many junk characters to " +
        "fill characters to use (will increase as neccesary), defaults to " +
        f"{SIZE_FAC_DEFAULT}",
        default=SIZE_FAC_DEFAULT,
        )
    parser.add_argument(
        "-b", "--intersect-bias",
        type=int,
        help="Set a bias toward or against word intersections. " +
        f"Defaults to {INTERSECT_BIAS_DEFAULT}, " +
        f"{INTERSECT_BIAS_NAMES[INTERSECT_BIAS_DEFAULT]} intersections",
        )
    parser.add_argument(
        "-a", "--answers",
        action="store_true",
        help="(CLI) Also print the puzzle with no filler characters",
        )
    parser.add_argument(
        "words",
        nargs="*",
        type=str,
        help="(CLI) Words to put into the puzzle, or '-' to accept stdin",
        )
    args = parser.parse_args()

    # We are CLI
    if args.words:
        # Allow for std piping
        if args.words == ["-"]:
            words = sys.stdin.read().strip().upper().split()
        else:
            words = [word.upper() for word in args.words]

        # Checkpoint for valid word entries
        for char in "".join(words):
            if char not in ALL_CHARS:
                print("Invalid characters detected in input")
                return 1

        # Generate!
        puzz, puzzkey = Generator().gen_word_search(
            words,
            directions=DIRECTIONS if args.use_hard else EASY_DIRECTIONS,
            size_fac=args.size_factor,
            intersect_bias=args.intersect_bias,
            )

        # Display the results
        print(puzz)

        # Optionally render the answer key
        if args.answers:
            # Put one blank line between puzzle and key
            print(f"\n{puzzkey}")

    # We are GUI
    else:
        if args.use_tk or not HAVE_QT:
            print("Using legacy Tk GUI")
            gui = tk_mainwindow

        else:
            gui = qt_mainwindow

        # Pass arguments to GUI
        if args.use_hard is not None:
            gui.GUICommon.Defaults.use_hard = args.use_hard
        if args.size_factor is not None:
            gui.GUICommon.Defaults.size_fac = args.size_factor
        if args.intersect_bias is not None:

            gui.GUICommon.Defaults.intersect_bias = args.intersect_bias

        # Launch
        try:
            gui.main()
            return 0
        except Exception as e:
            print(repr(e))
            return 2


# Run the app
if __name__ == "__main__":
    sys.exit(main())
