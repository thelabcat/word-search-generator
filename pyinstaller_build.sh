# Copyright 2025 Wilbur Jaywright d.b.a. Marswide BGL.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

echo "Preparing venv"
python -m venv ./.venv

echo "Activating venv"
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # cygwin is POSIX compatibility layer and Linux environment emulation for Windows
    os_suffix="linux"
    source ./.venv/bin/activate

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "WARNING: MacOS detected. Have not fully tested on MacOS."
    os_suffix="macos"
    source ./.venv/bin/activate

elif [[ "$OSTYPE" == "msys" ]]; then
    # Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
    # Used by Git Bash
    os_suffix="win"
    source ./.venv/Scripts/activate

elif [[ "$OSTYPE" == "freebsd"* ]]; then
    echo "WARNING: FreeBSD detected but not supported."
    os_suffix="freebsd"
    source ./.venv/bin/activate

else
    echo "Could not detect operating system. Guessing UNIX."
    os_suffix="unknown"
    source ./.venv/bin/activate
fi

progname="wordsearchgen"
output_name="$progname-$os_suffix-$(uname -m)"
echo "Executable output name determined to be $output_name"

echo "Installing requirements"
pip install -U -r requirements.txt
pip install -U setuptools pyinstaller

echo "Building exe"
# --icon=$progname.ico --add-data $progname.png:.
pyinstaller -w -F --name "$output_name" --hidden-import $progname.__main__ src/$progname\_wrap.py  2>&1 | tee pyinstaller_build_log.txt

echo "Cleaning up exe build residue"
rm -rf build
rm "$output_name.spec"

echo "Deactivating venv"
deactivate
