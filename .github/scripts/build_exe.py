"""Build the Word Search Generator executable with PyInstaller.

Usage (from the repo root, with the app and PyInstaller already installed):

    python .github/scripts/build_exe.py wordsearchgen-win-x86_64

The file lands in dist-exe/ (PyInstaller adds .exe on Windows by itself, so
leave .exe off the name). The app has no data files and makes no network
calls, so nothing needs bundling except the code.

S.D.G.
"""

import os
import sys

import PyInstaller.__main__

REPO = os.getcwd()


def main(name: str) -> None:
    args = [
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",  # No console window on Windows. Does nothing on Linux.
        "--name", name,
        "--hidden-import", "wordsearchgen.__main__",
        "--paths", os.path.join(REPO, "src"),
        "--distpath", os.path.join(REPO, "dist-exe"),
        "--workpath", os.path.join(REPO, "build-exe"),
        "--specpath", os.path.join(REPO, "build-exe"),
        os.path.join(REPO, "src", "wordsearchgen_wrap.py"),
    ]
    print("PyInstaller args:", args)
    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
