# Word Search Generator

This program is meant to help homeschoolers and commercial teachers alike create their own custom word search puzzles for the kids (or themselves). Word search puzzles are really great for the mind.

This program can be set to either use only the four easier left-to-right and downward directions (not including the down-left diagonal), or to use all eight directions when generating puzzles.

The source code runs as is. However, to run the code, you must install Python to run it, which you can download at python.org
This program was written for and successfully run in python 3.13.

This program also depends on the following Python libraries:
- [NumPy](https://pypi.org/project/numpy/)

For the newer Qt GUI, you should also install [PySide6](https://pypi.org/project/pyside6/), but it is currently not required.

You can find executables with bundled Python and dependencies in the Releases page of this repository.

## Installation and startup:

To run from source:
1. Download the repository as a zip, or clone it.
2. Download and install a version of Python 3, then use `pip` to install the dependencies. This can be expedited by downloading the `requirements.txt` file, then running `pip install -r requirements.txt` in the console.
3. Double-click the word_search_generator.py file (or otherwise open it with the Python interpreter on your OS).

To run from binary, download the appropriate binary for your OS from the Releases page, and double-click it.

Within a minute or so, a simple GUI with a text entry area should appear:

- The checkbox enables the use of non-European word placing directions.

- Size factor is the ratio of total puzzle letters to all letters that make up words. Cannot be less than 1. Defaults to 4. Entering 1 will make the most efficient puzzle possible, which will probably be ridiculously easy and is not recommended.

- The entry area has an explanatory line of text inserted at startup :) Delete that explanatory text, then enter one word per line with no punctuation. Capitalization will be ignored when generating the puzzle. Note: You technically don't have to enter one word per line as the program splits on _any_ whitespace and automatically strips trailing whitespace, but it will make your workflow potentially easier.

For now, wether using the new Qt GUI or the legacy Tkinter GUI, the features are about the same. The size factor spinbox behaves slightly differently in Tkinter, though. Note: You can force the Tkinter GUI even if you have PySide6 and thus Qt support, using a command line option (see below).


## Workflow:

1. Open a text editor (doesn't matter how fancy) and make your list of words. You can even use an empty word processor document you'll be placing the puzzle in later. Just remember, if you're putting the puzzle in above the list, leave a one line space to paste in.

2. Enter your list of words into the Word Search Generator, one word per line. You can copy paste from the word processor.

3. Change the program's settings as desired.

4. Click generate, then wait. The program may "freeze" for several seconds, but should not disappear (a crash).

5. A notification box will tell you that the puzzle generation was successful.

6. You can click OK, but if using Tkinter or X11, do not close the main program window, as this will erase what it copied to the clipboard.

7. Hop over to your word processor, and set the font to something monospaced (letters are all the same width). Examples: Consolas (I think), DejaVu Sans Mono, Freesans Mono, and any other fonts ending with "mono" are monospaced.

8. Paste (Ctrl+V on most systems). Ta-da!

9. The program will offer to let you also copy the puzzle key to the clipboard (and print it to stdout). Make sure you paste the puzzle out first before clicking "Yes"!

10. Include the word list, and you can close the generator program.

You can use "Justify Center" and font size options to make things look pretty :) Remember, only the actual puzzle need use the monospaced font. Everything else can be anything you like.

## Troubleshooting
### The puzzle does not actually copy to the clipboard, so pasting fails
You are probably using the Tkinter GUI on Wayland. Currently, my workaround for this on those systems is having the program print the puzzle to stdout, i.e. a terminal it was run from. There is much information elsewhere on how to run Python programs from the terminal. See [issue #1](https://github.com/thelabcat/word-search-generator/issues/1) for more information.

### Application fails to launch, and launching from CLI gives message about missing Qt plugin
You are probably using X11. See [issue #11](https://github.com/thelabcat/word-search-generator/issues/11) for more information, but the gist is it seems like Qt does not support X11 anymore. You can force the app to use TkInter instead with the `--tkinter` command line option.

### Size factor is not respected, allowing puzzle to be bigger than specified
This is intended behavior. Though it starts with a puzzle size determined from the size factor entered, the algorithm automatically increases the puzzle size if there was no way to fit all the words in.

## Command line options:
This program also supports several CLI options, including running without the GUI entirely. The program will go into CLI mode if and only if the `words` option is specified.

```
usage: word_search_generator.py [-h] [-t] [-H] [-s SIZE_FACTOR] [-a] [-d] [words ...]

Generate word search puzzles, CLI or GUI

positional arguments:
  words                 (CLI) Words to put into the puzzle, or '-' to accept stdin

options:
  -h, --help            show this help message and exit
  -t, --tkinter         (GUI) Use the legacy Tkinter GUI instead of Qt
  -H, --use-hard        (CLI) Use the harder, backwards (11-o'-clock) directions
  -s, --size-factor SIZE_FACTOR
                        (CLI) Set the starting factor of how many junk characters to fill characters to use (will increase as neccesary), defaults to 4
  -a, --answers         (CLI) Also print the puzzle with no filler characters
  -d, --no-decorate     (CLI) Don't print decoration lines around puzzle and key

S.D.G.
```

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
