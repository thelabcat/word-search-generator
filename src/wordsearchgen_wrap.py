#!/usr/bin/env python3
"""
Word Search Generator PyInstaller packing wrapper

Imports the wordsearchgen main app function and runs it.

S.D.G."""

import sys
from wordsearchgen import __main__

# Run the app
if __name__ == "__main__":
    sys.exit(__main__.main())
