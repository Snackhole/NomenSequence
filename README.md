# NomenSequence
NomenSequence is a simple GUI app to rename any files with ascending integers, and arbitrary prefixes, suffixes, and extensions, written in Python 3.14 with PyQT6.

## Installation
Because NomenSequence is written in 64-bit Python and packaged as an executable zip, a 64-bit Python 3 installation is required to run it.  It was written and tested in Python 3.14, though it may or may not run in other versions of Python 3.

### Windows
On Windows, an appropriate Python installation is included with the release, and does not need to be installed or downloaded separately.

Simply download the .zip file of the latest Windows release from this repository, unzip it wherever you like, and double-click on the `Create Shortcut.bat` file within the app folder.  This will create a shortcut in your Start menu that allows you to run the app.

### Linux
On Linux, NomenSequence has only been built and tested for Kubuntu 26.04.  It probably runs just fine on many other distros, but you're on your own as far as resolving any problems or differences.

It is generally assumed that you already have 64-bit Python 3 installed as part of your distro.  If your distro has 3.14, you should be fine; otherwise, you may or may not need to install 3.14.

First, download the .zip file of the latest Linux release from this repository, and unzip it wherever you like (probably easiest somewhere in your Home).  To run the app, open a terminal in the app's directory and use the following command:

```
python3 NomenSequence.pyzw
```

Alternatively, you can use the included Python interpreter (after giving `Python Interpreter - Linux/bin/python3` executable permissions, if needed):

```
"Python Interpreter - Linux/bin/python3" NomenSequence.pyzw
```

However, for convenience, consider running `python3 CreateLinuxDesktopFile.py` or `python3 CreateLinuxDesktopFileForIncludedInterpreter.py` (also in the app's directory; they will not work properly with any other working directory).  This will generate a .desktop file, which will then be moved to `~/.local/share/applications/`.  Now NomenSequence should show up along with your other apps in your desktop menus.

If you prefer not to use the included interpreter, consider deleting the `Python Interpreter - Linux` folder to save space.

If NomenSequence does not run at first, you probably need to resolve some dependencies.  First, try `sudo apt install libxcb-xinerama0`.  If that doesn't resolve the issue, try installing PyQT6 with `sudo apt install python3-pyqt6`; if this does resolve the issue, you might even be able to (partially) uninstall it with `sudo apt remove python3-pyqt6` and still run NomenSequence, as long as you don't autoremove the additional packages that were installed with it.  If installing PyQT6 through APT doesn't work, try installing it through pip; if you don't have pip already, use `sudo apt install python3-pip`, then run `pip3 install pyqt6`.  Other issues have not yet been encountered and will require you to do some research and troubleshooting to resolve on your system.

## Updates
Updating NomenSequence is as simple as deleting all files wherever you installed it *except* the `Configs` folder, and then extracting the contents of the latest release to the installation folder.  Any shortcuts in place should resolve without issue to the updated version.  If you are using the included interpreter, you may have to give it executable permissions after updating.

The `Configs` folder should be left in place as it stores settings and contexts between uses of the app.

## Uninstallation
Uninstalling NomenSequence itself only requires deleting the directory you extracted it to, along with any shortcuts you created.

If you need to uninstall Python 3.14 or, on Linux, PyQT6, consult their documentation.

## Building
Building NomenSequence from the source code in this repository requires the addition of the appropriate Python interpreter files, which are not included in this repository due to file size constraints on GitHub.

* For Windows builds, download the official Windows embeddable package (64-bit) for Python 3.14.4 from https://www.python.org/downloads/release/python-3144/.  Then, extract the contents of the `.zip` file, and recompress the contents as a `.tar.gz` file named `Python Interpreter - Windows.tar.gz`.  The files from the original `.zip` file should be at the top level of the `.tar.gz` file, not contained within a folder inside the archive.
* For Linux builds, download the file `cpython-3.14.4+20260414-x86_64-unknown-linux-gnu-install_only.tar.gz` from https://github.com/astral-sh/python-build-standalone/releases/tag/20260414.  Then, extract the contents of the downloaded `.tar.gz` file, and recompress the folders `bin`, `include`, `lib`, and `share` at the top level of a `.tar.gz` file named `Python Interpreter - Linux.tar.gz`.  Again, the folders from the downloaded `.tar.gz` file should be at the top level of the new `.tar.gz` file, not contained within a folder inside the archive.

For either OS, place the interpreter archive at the top level of the repository, and `Build.py` should be able to create usable builds.