# Word Search Generator

This program is meant to help homeschoolers and commercial teachers alike create their own custom word search puzzles for the kids (or themselves). Word search puzzles are really great for the mind.

This program can be set to either use the easier, top-bottom, left-right directions, or to use non-european AKA all directions when generating puzzles.

The source code runs as is. However, to run the code, you must install Python to run it, which you can download at python.org
Use the latest 3.x release. This program was written for and successfully run in python 3.8, but is expected to work with all 3.x verisons.


# INSTALLATION AND STARTUP:

Save the word_search_gen.pyw file somewhere. It will not output files when it runs, so your desktop is fine.

Download and install a version of Python 3 (probably will currently be 3.8, which works).

Double-click the word_search_gen.pyw file.

Within a minute or so, a simple GUI with a text entry area should appear:

- The checkbox enables the use of non-European word placing directions.

- Size factor is the ratio of total puzzle letters to all letters that make up words. Cannot be less than 1. Defaults to 4, and the arrow buttons won't take you past 2-9, although you CAN enter numbers outside this range. The GUI will round down floating-point numbers. Entering 1 will make the most efficient puzzle possible, which will probably be ridiculously easy and is not reccommended.

- The entry area has an explanatory line of text inserted at startup :) Delete that explanatory text, then enter one word per line with no punctuation. Capitalization will be ignored when generating the puzzle.


# WORKFLOW (steps with c at the number are critical, everything else is just my plan of doing it):

0) Open a text editor (doesn't matter how fancy) and make your list of words. You can even use an empty word processor document you'll be placing the puzzle in later. Just remember, if you're putting the puzzle in above the list, leave a one line space to paste in.

1c) Enter your list of words into the Word Search Generator, one word per line. You can copy paste from the word processor.

2c) Click generate, then wait. The program may "freeze" for several seconds, but should not disappear (a crash).

3c) A notification box will tell you that the puzzle generation was successful. Note: Though starting with a size determined from size_fac, the algorithm automatically increases puzzle size if there was no way to fit all the words in.

4c) Click OK, but DO NOT close the main program window, as this will erase what it copied to the system clipboard.

5c) Hop over to your word processor, and set the font to something monospaced (letters are all the same width). Examples: Consolas (I think), DejaVu Sans Mono, Freesans Mono, and any other fonts ending with "mono" are monospaced.

6c) Paste (Ctrl+V on most systems). Ta-da!

7) Include the word list, and you can close the generator program.

You can use "Justify Center" and font size options to make things look pretty :) Remember, only the actual puzzle need use the monospaced font. Everything else can be anything you like.

Solo Deo gloria. Amen.
