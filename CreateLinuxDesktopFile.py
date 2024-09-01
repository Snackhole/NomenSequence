import os
import shutil

AppName = "NomenSequence"

ExecutableZip = AppName + ".pyzw"
CurrentWorkingDirectory = os.getcwd()
AbsolutePathToExecutableZip = CurrentWorkingDirectory + "/" + ExecutableZip
AbsolutePathToIconPNG = CurrentWorkingDirectory + "/Assets/" + AppName + " Icon.png"

DesktopFileContents = f"""[Desktop Entry]
Type=Application
Name={AppName}
Exec=python3 "{AbsolutePathToExecutableZip}"
Icon={AbsolutePathToIconPNG}
Categories=Application;"""

CreatedDesktopFilePath = AppName + ".desktop"
DesktopFileDestinationPath = os.path.expanduser(os.path.join("~", ".local", "share", "applications", CreatedDesktopFilePath))

with open(CreatedDesktopFilePath, "w") as DesktopFile:
    DesktopFile.write(DesktopFileContents)

if os.path.isfile(DesktopFileDestinationPath):
    os.remove(DesktopFileDestinationPath)

shutil.move(CreatedDesktopFilePath, DesktopFileDestinationPath)
