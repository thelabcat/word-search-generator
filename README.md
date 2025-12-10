# Word Search Generator

![Screenshot](https://github.com/thelabcat/word-search-generator/blob/main/qt_main_window_screenshot.png?raw=true "The main app window, Qt version")

This program takes a list of words, and automatically generates a word search puzzle from them.

This program can be set to either use only the four easier left-to-right and downward directions (not including the down-left diagonal), or to use all eight directions when generating puzzles.

There are two main ways to run this program. You can install the PyPi package, or download a bundled executable.

Since Python is an interpreted language, the source code can run without being compiled. However, to run the code, you must install Python, which you can download at https://python.org .
This program is currently maintained in Python 3.13. If you need to use an older Python and you encounter a compatibility issue, let me know, and I will seriously consider implementing backwards compatibility for your use case.

This program also depends on the following Python libraries:
- [NumPy](https://pypi.org/project/numpy/)
- [PySide6](https://pypi.org/project/pyside6/) (weak dependency, needed only for the Qt version of the GUI)

If you download this package from PyPi (after installing Python), the dependencies will be installed automatically. You can also import the algorithm as a library to use in your own projects. The PyPi version of the program script and the library name to import are `wordsearchgen`.

You can find executables with bundled Python and dependencies in the Releases page of this repository.

## Installation and startup:

To run from source:
1. Download and install a version of Python 3 if it is not already installed. On Linux, it probably is.
2. If you are not on Microsoft Windows, you will likely need to install Python 3 Pip separately. Do so now.
3. Install the package with `pip install word-search-app`.

To run from a binary, things are a bit simpler. Download the appropriate binary for your OS from the Releases page of the GitHub repository, and double-click it.

Within a minute or so, a simple GUI with a text entry area should appear:

- The checkbox enables the use of harder-to-find word placing directions (ones that go backwards). The easy-to-find directions, which are always used, are right-hand, down, right-hand down, and right-hand up. The optional harder directions are up, left-hand, left-hand up, and left-hand down.

- Size factor is the target ratio of total puzzle letters to all letters that make up words. Cannot be less than 1. Defaults to 4. Entering 1 will make the most efficient puzzle possible, which will probably be ridiculously easy and is not recommended. The generator will automatically increase the puzzle size as necessary to fit in all the words, so this size factor is merely a starting size which may or may not be kept.

- Word intersection bias can tell the program to try word positions in the order of how many times that word legally intersects other already-placed words, either with lowest or highest first. The default "Random" does not do any kind of ordering, so just by probability you are probably going to get less than half of the possible intersections with "Random" set. Setting the bias to "Prefer" can speed up puzzle generation with small size factors, since it naturally crowds words together as tightly as possible.

- The entry area has an explanatory set of demo words inserted at startup :) Delete that explanatory text, then enter one word per line with no punctuation. Capitalization will be ignored when generating the puzzle. Duplicate words will also be ignored. Tip: If using some other whitespace than new lines is easier in your case, don't worry. The text area will convert those automatically. It will also quietly filter out punctuation. Note: As a test, you can run generation with the explanatory demo words.

I have done my best to make the Tk and Qt GUIs function identically. Tk is X11 native only right now, so the clipboard feature may not work properly on Wayland. Qt can run on X11 or Wayland, but is not easily available on some platforms. If the app cannot find the PySide6 library, i.e. PyQt support, it will automatically launch the Tk GUI instead. You can force the Tk GUI even if you have PySide6 by using a command line option (see below).


## Workflow:

1. Open a text editor (doesn't matter how fancy) and make your list of words. You can even use an empty word processor document you'll be placing the puzzle in later. Just remember, if you're putting the puzzle in above the list, leave a one line space to paste in.

2. Enter or paste (<kbd>Ctrl</kbd> + <kbd>V</kbd>) your list of words into the Word Search Generator. It should automatically adjust the input text so there is exactly one word per line. Note: There is no right-click edit menu at current, at least not in the Tk GUI. To copy or paste in the generator's text area, you must use the <kbd>Ctrl</kbd> + <kbd>C</kbd> and <kbd>Ctrl</kbd> + <kbd>V</kbd> keyboard shortcuts.

3. Change the generator's settings as desired.

4. Click "Generate", then wait for the algorithm to work. The "Generate" button should instantly change to "Cancel", and the progress bar will show how many words have been placed so far out of all of them. Note: This is not a true "progress" bar, as it will occasionally jump backwards if changes are reverted and new possibility branches are tried. This happens more often with greater word numbers and smaller size factors, as the program is less likely to find a working combination.

5. Once the generation has finished, the "Cancel" button will change back to "Generate", and the two "Copy" buttons will un-grey.

6. Click "Copy puzzle". If using Tk or X11, do not close the main program window, as this will erase what it copied to the clipboard.

7. Hop over to your word processor, and set the font to something monospaced (letters are all the same width). Examples: Consolas (I think), DejaVu Sans Mono, Freesans Mono, and any other fonts ending with "mono" are monospaced.

8. Paste (<kbd>Ctrl</kbd> + <kbd>V</kbd>). Ta-da!

9. If desired, repeat steps 6-8, but click "Copy answer key" instead. This will copy a version of the generated puzzle without the filler characters.

10. Include the word list, and you can close the generator program.

You can use "Justify Center" and font size options to make things look pretty :) Remember, only the actual puzzle need use the monospaced font. Everything else can be anything you like.

## Troubleshooting
### I cannot install via Pip on Linux, with an error about my environment being externally managed
If your main Python environment is managed "externally" (I.E. by your system package manager), you can't use `pip` without a virtual environment. Such an environment is usually pretty easy to set up. One command creates a virtual environment, and a second activates it for any terminal session. Look into how to use the Python `venv` library.

### The puzzle does not actually copy to the clipboard, so pasting fails
You are probably using the Tk GUI on Wayland. To get around this without installing anything, run the program from / with the command line. Clicking the result buttons will also print the puzzle to Standard Output (I.E. the command line window). See [issue #1](https://github.com/thelabcat/word-search-generator/issues/1) for more information.

### Application fails to launch from source on Linux, and launching from CLI gives message about missing Qt plugin
You are probably using X11. See [issue #11](https://github.com/thelabcat/word-search-generator/issues/11) for more information. You can force the app to use Tk instead with the `--use-tk` command line option, or just run the app with no GUI, or try to install [these dependencies for Qt 6 on X11](https://doc.qt.io/qt-6/linux-requirements.html). Note: The bundled Linux executable should have these dependencies inside it, so if you are having this issue while using the Linux bundled executable, let me know.

### Size factor is not respected, allowing puzzle to be bigger than specified
This is intended behavior. Though it starts with a puzzle size determined from the size factor entered, the algorithm automatically increases the puzzle size if there was no way to fit all the words in.

### I cannot copy / paste in the word entry area with right-click
This is expected, though not intended, behavior. You are probably using the Tk GUI, which does not have a right-click menu by default for its Text widget. I may implement one in the future, but for now you will have to yse keyboard shortcuts. Usually, this is <kbd>Ctrl</kbd> + <kbd>C</kbd> for copy, and <kbd>Ctrl</kbd> + <kbd>V</kbd> for paste.

### Words entered more than once only appear once in the puzzle
This is intended behavior, and is a limitation of the algorithm. If you really want multiple word support, let me know.

## Command line options:
This program also supports several CLI options, including running without the GUI entirely. The program will go into CLI mode if and only if the `words` option is specified.

```
usage: wordsearchgen [-h] [-t] [-H] [-s SIZE_FACTOR] [-b INTERSECT_BIAS] [-a] [words ...]

Generate word search puzzles, CLI or GUI. CLI mode is triggered by passing any words to the command.

positional arguments:
  words                 (CLI) Words to put into the puzzle, or '-' to accept stdin

options:
  -h, --help            show this help message and exit
  -t, --use-tk          (GUI) Use the legacy Tk GUI instead of Qt
  -H, --use-hard        Use the harder, backwards (11-o'-clock) directions
  -s, --size-factor SIZE_FACTOR
                        Set the starting factor of how many junk characters to fill characters to use (will increase as neccesary), defaults to 4
  -b, --intersect-bias INTERSECT_BIAS
                        Set a bias toward or against word intersections. Defaults to 0, random intersections
  -a, --answers         (CLI) Also print the puzzle with no filler characters

S.D.G.

```

Note that the options which affect the GUI (anything not labeled CLI other than `--help`) merely set its defaults. They can still be overridden graphically.

## Legal:

Various parts of this repository are under different licenses, usually marked at the top of the file.

This readme file is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Solo Deo gloria. Amen.
