import os

AppName = "NomenSequence"
ExecutableZip = AppName + ".pyzw"
CurrentWorkingDirectory = os.getcwd()
AbsolutePathToExecutableZip = CurrentWorkingDirectory + "/" + ExecutableZip
AbsolutePathToIconPNG = CurrentWorkingDirectory + "/Assets/NomenSequence Icon.png"

DesktopFileContents = """[Desktop Entry]
Type=Application
Name={0}
Exec=python3 "{1}"
Icon={2}
Categories=Application;"""
DesktopFileContents = DesktopFileContents.format(AppName, AbsolutePathToExecutableZip, AbsolutePathToIconPNG)

with open(AppName + ".desktop", "w") as DesktopFile:
    DesktopFile.write(DesktopFileContents)