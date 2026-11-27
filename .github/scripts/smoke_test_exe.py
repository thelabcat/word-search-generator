"""Smoke test a built Word Search Generator executable. Fails loudly if off.

Usage: python .github/scripts/smoke_test_exe.py dist-exe/wordsearchgen-win-x86_64.exe

1. Command line mode: generates a puzzle (a bad word must be refused with exit
   code 1, good words must give exit code 0 and, where the platform lets a
   program print, a puzzle).
2. GUI mode, Qt (default) and Tk (--use-tk): starts the program and checks it
   really opens its window (Windows) or stays running (Linux: run this under
   xvfb-run so there is a display).

S.D.G.
"""

import os
import subprocess
import sys
import tempfile
import time

WINDOW_TITLE = "Word Search Gen"
"""The title of the app window, as set in gui_common.py"""

IS_WINDOWS = os.name == "nt"


def cli_test(exe: str) -> None:
    bad = subprocess.run([exe, "-a", "HE-LLO"], capture_output=True, timeout=120)
    print("bad word exit code:", bad.returncode)
    assert bad.returncode == 1, "A word with a bad character should exit with code 1"

    good = subprocess.run([exe, "-a", "HELLO", "WORLD", "PYTHON"], capture_output=True, timeout=120)
    out = good.stdout.decode(errors="replace")
    print("good words exit code:", good.returncode)
    assert good.returncode == 0, "Generating a puzzle failed: " + good.stderr.decode(errors="replace")
    if IS_WINDOWS:
        # A windowed program has no console to print to, so the exit code is all we have
        print("Windowed program: not checking the printed puzzle.")
    else:
        print(out)
        letters = "".join(out.split())
        for word in ("HELLO", "WORLD", "PYTHON"):
            # The answer key shows each word's letters in place, in order
            assert all(c in letters for c in set(word)), "Puzzle is missing letters of " + word
        assert len(out.splitlines()) > 5, "The puzzle output is too short"
    print("CLI test passed.")


def window_titles() -> list:
    """Titles of all visible top level windows (Windows only)"""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    titles = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def collect(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                titles.append(buf.value)
        return True

    user32.EnumWindows(collect, 0)
    return titles


def gui_test(exe: str, extra_args: list, label: str) -> None:
    # Keep what the program says on stderr, to catch a Qt that silently fell back to Tk
    errfile = tempfile.TemporaryFile()
    proc = subprocess.Popen([exe] + extra_args, stderr=errfile)
    try:
        if IS_WINDOWS:
            deadline = time.time() + 60
            seen = []
            while time.time() < deadline:
                time.sleep(2)
                seen = window_titles()
                if WINDOW_TITLE in seen:
                    print(f"GUI test passed ({label}): the window opened.")
                    return
                assert proc.poll() is None, f"The program exited before its {label} window opened"
            raise AssertionError(f"No {label} window after 60 s. Visible windows: " + repr(seen))
        else:
            time.sleep(15)
            assert proc.poll() is None, f"The {label} GUI exited within 15 s with code {proc.returncode}"
            errfile.seek(0)
            said = errfile.read().decode(errors="replace")
            print(f"{label} GUI stderr: {said!r}")
            assert "Could not import the Qt GUI module" not in said, "Qt did not load (the program fell back to Tk)"
            print(f"GUI test passed ({label}): still running after 15 s.")
    finally:
        # Kill the whole tree: onefile programs start a child process
        if IS_WINDOWS:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        else:
            subprocess.run(["pkill", "-P", str(proc.pid)], capture_output=True)
            proc.kill()
        proc.wait()


def main(exe: str) -> None:
    exe = os.path.abspath(exe)
    assert os.path.exists(exe), "No executable at " + exe
    print("Testing", exe, os.path.getsize(exe), "bytes")
    cli_test(exe)
    gui_test(exe, [], "Qt")
    gui_test(exe, ["--use-tk"], "Tk")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
