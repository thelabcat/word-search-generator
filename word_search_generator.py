#!/usr/bin/env python3
"""Word Search Generator main

Generate word search puzzles with a GUI or a CLI

This file is part of Word Search Generator.

Word Search Generator is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>."""

import argparse
from algorithm import (
    Generator,
    ALL_CHARS,
    DIRECTIONS,
    EASY_DIRECTIONS,
    SIZE_FAC_DEFAULT,
    )

try:
    from qt_mainwindow import main as qtmain
    HAVE_QT = True
except ImportError as e:
    print("Could not import the Qt GUI module:")
    print(e)
    HAVE_QT = False

from tk_mainwindow import main as tkmain

# If this program was launched directly, run it
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Word Search Generator",
        description="Generate word search puzzles, CLI or GUI",
        epilog="S.D.G.")

    parser.add_argument("-t", "--tkinter", action="store_true", help="(GUI) Use the legacy Tkinter GUI instead of Qt")
    parser.add_argument("-H", "--use-hard", action="store_true", help="(CLI) Use the harder, backwards (11-o'-clock) directions")
    parser.add_argument("-s", "--size-factor", type=int, help="(CLI) Set the starting size factor", default=SIZE_FAC_DEFAULT)
    parser.add_argument("-a", "--answers", action="store_true", help="(CLI) Also print the puzzle with no filler characters")
    parser.add_argument("words", nargs="*", type=str, help="(CLI) Words to put into the puzzle")
    args = parser.parse_args()

    # We are CLI
    if args.words:
        # Checkpoint for valid word entries
        for char in "".join(args.words).upper():
            assert char in ALL_CHARS, "Invalid characters detected in input"

        table = Generator.gen_word_search(
            [word.upper() for word in args.words],
            directions=DIRECTIONS if args.use_hard else EASY_DIRECTIONS,
            size_fac=args.size_factor,
            )

        # Render the puzzle
        print("--- Puzzle ---")
        print(Generator.render_puzzle(table))
        print("--------------")

        # Optionally render the answer key
        if args.answers:
            print("- Answer Key -")
            print(Generator.render_puzzle(table, fill=False))
            print("--------------")

    # We are GUI
    elif args.tkinter or not HAVE_QT:
        print("Using legacy Tkinter GUI")
        tkmain()

    else:
        qtmain()
