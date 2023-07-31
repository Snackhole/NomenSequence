# NomenSequence
NomenSequence is a simple GUI app to rename any files with ascending integers, and arbitrary prefixes, suffixes, and extensions, written in Python 3.10 with PyQT5.

## Installation
Because NomenSequence is written in 64-bit Python and packaged as an executable zip, a 64-bit Python 3 installation is required to run it.  It was written and tested in Python 3.10, though it may or may not run in other versions of Python 3.

### Windows
On Windows, an appropriate Python installation is included with the release, and does not need to be installed or downloaded separately.

Simply download the .zip file of the latest Windows release from this repository, unzip it wherever you like, and double-click on the `Create Shortcut.bat` file within the app folder.  This will create a shortcut that allows you to run the app.

It is recommended you place the shortcut in `\AppData\Roaming\Microsoft\Windows\Start Menu\Programs` for convenience.  This will cause the shortcut to appear in the Start menu with the correct icon.  More shortcuts can always be made by double-clicking on `Create Shortcut.bat`.

### Linux
On Linux, NomenSequence has only been built and tested for Kubuntu 22.04.  It probably runs just fine on many other distros, but you're on your own as far as resolving any problems or differences.

It is generally assumed that you already have 64-bit Python 3 installed as part of your distro.  If your distro has 3.10, you should be fine; otherwise, you may or may not need to install 3.10.

First, download the .zip file of the latest Linux release from this repository, and unzip it wherever you like (probably easiest somewhere in your Home).  To run the app, open a terminal in the app's directory and use the following command:

```
python3 NomenSequence.pyzw
```

Alternatively, you can use the included Python interpreter (after giving `Python Interpreter - Linux/bin/python3` executable permissions):

```
"Python Interpreter - Linux/bin/python3" NomenSequence.pyzw
```

However, for convenience, consider running `python3 CreateLinuxDesktopFile.py` or `python3 CreateLinuxDesktopFileForIncludedInterpreter.py` (also in the app's directory; they will not work properly with any other working directory).  This will generate a .desktop file, which you should then copy to `usr/share/applications`  with `sudo cp NomenSequence.desktop /usr/share/applications`.  Now NomenSequence should show up along with your other apps in your desktop menus.

If you prefer not to use the included interpreter, consider deleting the `Python Interpreter - Linux` folder to save space.

If NomenSequence does not run at first, you probably need to resolve some dependencies.  First, try `sudo apt install libxcb-xinerama0`.  If that doesn't resolve the issue, try installing PyQT5 with `sudo apt install python3-pyqt5`; if this does resolve the issue, you might even be able to (partially) uninstall it with `sudo apt remove python3-pyqt5` and still run NomenSequence, as long as you don't autoremove the additional packages that were installed with it.  If installing PyQT5 through APT doesn't work, try installing it through pip; if you don't have pip already, use `sudo apt install python3-pip`, then run `pip3 install pyqt5`.  Other issues have not yet been encountered and will require you to do some research and troubleshooting to resolve on your system.

## Updates
Updating NomenSequence is as simple as deleting all files wherever you installed it *except* the `Configs` folder, and then extracting the contents of the latest release to the installation folder.  Any shortcuts in place should resolve without issue to the updated version.  If you are using the included interpreter, you likely must give it executable permissions after updating.

The `Configs` folder should be left in place as it stores settings and contexts between uses of the app.

## Uninstallation
Uninstalling NomenSequence itself only requires deleting the directory you extracted it to, along with any shortcuts you created.

If you need to uninstall Python 3.10 or, on Linux, PyQT5, consult their documentation.