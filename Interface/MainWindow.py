import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QMainWindow, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath

        # Variables
        self.RenameInProgress = False

        # Initialize
        super().__init__()

        # Create Interface
        self.CreateInterface()

        # Show Window
        self.show()

        # Center Window
        self.Center()

        # Load Configs
        self.LoadConfigs()

    def CreateInterface(self):
        # Create Window Icon
        self.WindowIcon = QIcon(self.GetResourcePath("Assets/NomenSequence Icon.png"))

        # Window Icon and Title
        self.setWindowIcon(self.WindowIcon)
        self.setWindowTitle(self.ScriptName)

        # Create Central Frame
        self.Frame = QFrame()

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

    def GetResourcePath(self, RelativeLocation):
        return os.path.join(self.AbsoluteDirectoryPath, RelativeLocation)

    def Center(self):
        pass

    def LoadConfigs(self):
        # Last Opened Directory
        LastOpenedDirectoryFile = self.GetResourcePath("Configs/LastOpenedDirectory.cfg")
        if os.path.isfile(LastOpenedDirectoryFile):
            with open(LastOpenedDirectoryFile, "r") as ConfigFile:
                self.LastOpenedDirectory = ConfigFile.readline()
        else:
            self.LastOpenedDirectory = None

    def SaveConfigs(self):
        if not os.path.isdir(self.GetResourcePath("Configs")):
            os.mkdir(self.GetResourcePath("Configs"))

        # Last Opened Directory
        if type(self.LastOpenedDirectory) == str:
            if os.path.isdir(self.LastOpenedDirectory):
                with open(self.GetResourcePath("Configs/LastOpenedDirectory.cfg"), "w") as ConfigFile:
                    ConfigFile.write(self.LastOpenedDirectory)

    def DisplayMessageBox(self, Message, Icon=QMessageBox.Information, Buttons=QMessageBox.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec_()

    # Window Management Methods
    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        DesktopCenterPoint = QApplication.primaryScreen().availableGeometry().center()
        FrameGeometryRectangle.moveCenter(DesktopCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())

    def closeEvent(self, Event):
        Close = True
        if self.RenameInProgress:
            Close = self.DisplayMessageBox("Files are currently being renamed.  Exit anyway?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.Yes
        if Close:
            self.SaveConfigs()
            Event.accept()
        else:
            Event.ignore()
