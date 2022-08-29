import os
import platform
import shutil
import subprocess

import zipapp


# Build Variables
BuildVariables = {}
BuildVariables["Version"] = "2"
BuildVariables["AppName"] = "NomenSequence"
BuildVariables["VersionedAppName"] = BuildVariables["AppName"] + " " + BuildVariables["Version"]


def Build():
    # Build Functions
    def CopyFilesToBuildFolder(CopiedFiles):
        if "BuildFolder" in BuildVariables:
            IgnoredFiles = [File for File in os.listdir(".") if File not in CopiedFiles]
            shutil.copytree(".", BuildVariables["BuildFolder"], ignore=lambda Source, Contents: IgnoredFiles)

    def UnzipArchivedFilesToBuildFolder(ArchivedFiles):
        if "BuildFolder" in BuildVariables:
            for Archive in ArchivedFiles:
                shutil.unpack_archive(Archive, os.path.join(BuildVariables["BuildFolder"], os.path.splitext(Archive)[0]))

    def CleanUp():
        if "BuildFolder" in BuildVariables:
            shutil.rmtree(BuildVariables["BuildFolder"])
            print("Build files cleaned up.")

    # Additional Build Variables
    BuildVariables["BuildFolder"] = "BUILD - " + BuildVariables["VersionedAppName"]
    BuildVariables["OS"] = platform.system()
    if BuildVariables["OS"] not in ["Windows", "Linux"]:
        print("OS unsupported; you'll have to write your own build function to package on this OS.")
        return

    BuildVariables["CodeFiles"] = ["Core", "Interface", "Build.py", "NomenSequence.py"]
    BuildVariables["AssetFiles"] = ["Assets"]
    BuildVariables["ArchivedFiles"] = []

    BuildVariables["ExecutableZipName"] = BuildVariables["AppName"] + ".pyzw"
    BuildVariables["Interpreter"] = "python3"
    BuildVariables["Main"] = BuildVariables["AppName"] + ":StartApp"

    BuildVariables["CurrentWorkingDirectory"] = os.getcwd()

    #  Windows-Specific Build Variables
    if BuildVariables["OS"] == "Windows":
        BuildVariables["Command"] = "python -m pip install -r \"" + BuildVariables["CurrentWorkingDirectory"] + "\\requirements.txt\" --target \"" + BuildVariables["CurrentWorkingDirectory"] + "\\" + BuildVariables["BuildFolder"] + "\""
        BuildVariables["AssetFiles"].append("Create Shortcut.bat")
        BuildVariables["ArchivedFiles"].append("Python Interpreter.zip")

    # Linux-Specific Build Variables
    if BuildVariables["OS"] == "Linux":
        BuildVariables["Command"] = "pip3 install -r \"" + BuildVariables["CurrentWorkingDirectory"] + "/requirements.txt\" --target \"" + BuildVariables["CurrentWorkingDirectory"] + "/" + BuildVariables["BuildFolder"] + "\""
        BuildVariables["AssetFiles"].append("CreateLinuxDesktopFile.py")

    # Copy Code to Build Folder
    CopyFilesToBuildFolder(BuildVariables["CodeFiles"])
    print("Code files copied to build folder.")

    # Create Executable Archive
    zipapp.create_archive(BuildVariables["BuildFolder"], BuildVariables["ExecutableZipName"], BuildVariables["Interpreter"], BuildVariables["Main"])
    print("Executable archive created.")

    # Delete Build Folder
    shutil.rmtree(BuildVariables["BuildFolder"])
    print("Build folder deleted.")

    # Copy Assets to Build Folder and Move Executable Zip
    CopyFilesToBuildFolder(BuildVariables["AssetFiles"])
    print("Assets copied to build folder.")
    shutil.move(BuildVariables["ExecutableZipName"], BuildVariables["BuildFolder"])
    print("Executable archive moved to build folder.")

    # Unzip Archived Files to Build Folder
    UnzipArchivedFilesToBuildFolder(BuildVariables["ArchivedFiles"])
    print("Archived files moved to build folder.")

    # Install Dependencies
    DependenciesProcess = subprocess.run(BuildVariables["Command"], shell=True)
    if DependenciesProcess.returncode != 0:
        print("Build error while installing dependencies; cleaning up.")
        CleanUp()
        return

    # Zip Build
    shutil.make_archive(BuildVariables["VersionedAppName"] + " - " + BuildVariables["OS"], "zip", BuildVariables["BuildFolder"])
    print("Build zipped.")

    # Clean Up
    CleanUp()
    print("Build complete.")


if __name__ == "__main__":
    Build()
