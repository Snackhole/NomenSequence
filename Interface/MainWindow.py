import copy
import json
import math
import os
import threading

from PyQt6 import QtCore
from PyQt6.QtGui import QIcon, QAction, QColor, QPalette
from PyQt6.QtWidgets import QApplication, QFileDialog, QFrame, QGridLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton, QSpinBox, QInputDialog

from Core.Renamer import Renamer
from Interface.StatusThread import StatusThread
from Interface.Widgets.IconButtons import AddButton, DeleteButton, MoveDownButton, MoveUpButton
from Interface.Widgets.QueueTreeWidget import QueueTreeWidget


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath, AppInst):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath
        self.AppInst = AppInst

        # Variables
        self.RestrictedCharacters = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]
        self.RenameInProgress = False

        # Initialize
        super().__init__()

        # Create Renamer
        self.Renamer = Renamer()

        # Create Interface
        self.CreateInterface()
        self.show()

        # Center Window
        self.Center()

        # Load Configs
        self.LoadConfigs()

        # Update Queue
        self.UpdateQueue()

    def CreateInterface(self):
        # Load Theme
        self.LoadTheme()

        # Create Window Icon
        self.WindowIcon = QIcon(self.GetResourcePath("Assets/NomenSequence Icon.png"))

        # Window Icon and Title
        self.setWindowIcon(self.WindowIcon)
        self.setWindowTitle(self.ScriptName)

        # Create Central Frame
        self.Frame = QFrame()

        # Create Widgets
        self.QueueTreeWidget = QueueTreeWidget(self)
        self.AddToQueueButton = AddButton(Slot=self.AddToQueue, Tooltip="Add Files to Rename Queue")
        self.RemoveFromQueueButton = DeleteButton(Slot=self.RemoveFromQueue, Tooltip="Remove File from Rename Queue")
        self.MoveFileUpInQueueButton = MoveUpButton(Slot=self.MoveFileUp, Tooltip="Move File Up in Queue")
        self.MoveFileDownInQueueButton = MoveDownButton(Slot=self.MoveFileDown, Tooltip="Move File Down in Queue")
        self.ClearQueueButton = QPushButton("Clear Queue")
        self.ClearQueueButton.clicked.connect(self.ClearQueue)
        self.PrefixLineEdit = QLineEdit()
        self.PrefixLineEdit.setPlaceholderText("Prefix")
        self.PrefixLineEdit.textChanged.connect(self.UpdateQueue)
        self.NumberStartSpinBox = QSpinBox()
        self.NumberStartSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.NumberStartSpinBox.setButtonSymbols(self.NumberStartSpinBox.ButtonSymbols.NoButtons)
        self.NumberStartSpinBox.setRange(0, 1000000000)
        self.NumberStartSpinBox.setPrefix("Start at:  ")
        self.NumberStartSpinBox.setValue(1)
        self.NumberStartSpinBox.valueChanged.connect(self.UpdateQueue)
        self.SuffixLineEdit = QLineEdit()
        self.SuffixLineEdit.setPlaceholderText("Suffix")
        self.SuffixLineEdit.textChanged.connect(self.UpdateQueue)
        self.ExtensionLineEdit = QLineEdit()
        self.ExtensionLineEdit.setPlaceholderText("Extension")
        self.ExtensionLineEdit.textChanged.connect(self.UpdateQueue)
        self.ExtraDigitsSpinBox = QSpinBox()
        self.ExtraDigitsSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ExtraDigitsSpinBox.setButtonSymbols(self.ExtraDigitsSpinBox.ButtonSymbols.NoButtons)
        self.ExtraDigitsSpinBox.setRange(0, 1000000000)
        self.ExtraDigitsSpinBox.setPrefix("Extra digits:  ")
        self.ExtraDigitsSpinBox.setValue(0)
        self.ExtraDigitsSpinBox.valueChanged.connect(self.UpdateQueue)
        self.RenameButton = QPushButton("Rename Files")
        self.RenameButton.clicked.connect(self.Rename)
        self.ProgressSeparator = QFrame()
        self.ProgressSeparator.setFrameShape(QFrame.Shape.HLine)
        self.ProgressSeparator.setFrameShadow(QFrame.Shadow.Sunken)
        self.RenameProgressLabel = QLabel("Rename Progress")
        self.RenameProgressBar = QProgressBar()

        # Widgets to Disable While Renaming
        self.DisableList = []
        self.DisableList.append(self.AddToQueueButton)
        self.DisableList.append(self.RemoveFromQueueButton)
        self.DisableList.append(self.MoveFileUpInQueueButton)
        self.DisableList.append(self.MoveFileDownInQueueButton)
        self.DisableList.append(self.ClearQueueButton)
        self.DisableList.append(self.PrefixLineEdit)
        self.DisableList.append(self.NumberStartSpinBox)
        self.DisableList.append(self.SuffixLineEdit)
        self.DisableList.append(self.ExtensionLineEdit)
        self.DisableList.append(self.RenameButton)

        # Create Layout
        self.Layout = QGridLayout()

        # Widgets in Layout
        self.Layout.addWidget(self.AddToQueueButton, 0, 0)
        self.Layout.addWidget(self.RemoveFromQueueButton, 0, 1)
        self.Layout.addWidget(self.MoveFileUpInQueueButton, 0, 2)
        self.Layout.addWidget(self.MoveFileDownInQueueButton, 0, 3)
        self.Layout.addWidget(self.ClearQueueButton, 0, 4)
        self.Layout.addWidget(self.QueueTreeWidget, 1, 0, 1, 5)
        self.InputsLayout = QGridLayout()
        self.InputsLayout.addWidget(self.PrefixLineEdit, 0, 0)
        self.InputsLayout.addWidget(self.NumberStartSpinBox, 0, 1)
        self.InputsLayout.addWidget(self.SuffixLineEdit, 0, 2)
        self.InputsLayout.addWidget(self.ExtensionLineEdit, 0, 3)
        self.InputsLayout.addWidget(self.ExtraDigitsSpinBox, 0, 4)
        self.InputsLayout.addWidget(self.RenameButton, 1, 0, 1, 5)
        for Column in [0, 2, 3]:
            self.InputsLayout.setColumnStretch(Column, 1)
        self.Layout.addLayout(self.InputsLayout, 2, 0, 1, 5)
        self.Layout.addWidget(self.ProgressSeparator, 3, 0, 1, 5)
        self.ProgressLayout = QGridLayout()
        self.ProgressLayout.addWidget(self.RenameProgressLabel, 0, 0)
        self.ProgressLayout.addWidget(self.RenameProgressBar, 0, 1)
        self.Layout.addLayout(self.ProgressLayout, 4, 0, 1, 5)

        # Set and Configure Layout
        self.Frame.setLayout(self.Layout)

        # Create Actions
        self.CreateActions()

        # Create Menu Bar
        self.CreateMenuBar()

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

        # Create Keybindings
        self.CreateKeybindings()

    def CreateActions(self):
        self.SetThemeAction = QAction("Set Theme")
        self.SetThemeAction.triggered.connect(self.SetTheme)

        self.QuitAction = QAction("Quit")
        self.QuitAction.triggered.connect(self.close)

    def CreateMenuBar(self):
        self.MenuBar = self.menuBar()

        self.FileMenu = self.MenuBar.addMenu("File")
        self.FileMenu.addAction(self.SetThemeAction)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.QuitAction)

    def CreateKeybindings(self):
        self.DefaultKeybindings = {}
        self.DefaultKeybindings["QuitAction"] = "Ctrl+Q"

    def GetResourcePath(self, RelativeLocation):
        return os.path.join(self.AbsoluteDirectoryPath, RelativeLocation)

    def LoadConfigs(self):
        # Last Opened Directory
        LastOpenedDirectoryFile = self.GetResourcePath("Configs/LastOpenedDirectory.cfg")
        if os.path.isfile(LastOpenedDirectoryFile):
            with open(LastOpenedDirectoryFile, "r") as ConfigFile:
                self.LastOpenedDirectory = ConfigFile.readline()
        else:
            self.LastOpenedDirectory = None

        # Keybindings
        KeybindingsFile = self.GetResourcePath("Configs/Keybindings.cfg")
        if os.path.isfile(KeybindingsFile):
            with open(KeybindingsFile, "r") as ConfigFile:
                self.Keybindings = json.loads(ConfigFile.read())
        else:
            self.Keybindings = copy.deepcopy(self.DefaultKeybindings)
        for Action, Keybinding in self.DefaultKeybindings.items():
            if Action not in self.Keybindings:
                self.Keybindings[Action] = Keybinding
        InvalidBindings = []
        for Action in self.Keybindings.keys():
            if Action not in self.DefaultKeybindings:
                InvalidBindings.append(Action)
        for InvalidBinding in InvalidBindings:
            del self.Keybindings[InvalidBinding]
        for Action, Keybinding in self.Keybindings.items():
            getattr(self, Action).setShortcut(Keybinding)

    def SaveConfigs(self):
        if not os.path.isdir(self.GetResourcePath("Configs")):
            os.mkdir(self.GetResourcePath("Configs"))

        # Last Opened Directory
        if type(self.LastOpenedDirectory) == str:
            if os.path.isdir(self.LastOpenedDirectory):
                with open(self.GetResourcePath("Configs/LastOpenedDirectory.cfg"), "w") as ConfigFile:
                    ConfigFile.write(self.LastOpenedDirectory)

        # Keybindings
        with open(self.GetResourcePath("Configs/Keybindings.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.Keybindings, indent=2))

        # Theme
        with open(self.GetResourcePath("Configs/Theme.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.Theme))

    def AddToQueue(self):
        FilesToAdd = QFileDialog.getOpenFileNames(caption="Files to Add to Queue", directory=self.LastOpenedDirectory)[0]
        if len(FilesToAdd) < 1:
            return
        AllFilesAddedSuccessfully = self.Renamer.AddFilesToQueue(FilesToAdd)
        self.UpdateQueue()
        self.LastOpenedDirectory = os.path.dirname(FilesToAdd[0])
        if not AllFilesAddedSuccessfully:
            self.DisplayMessageBox("Some of the selected files could not be added to the queue.  They may have already been in the queue.", Icon=QMessageBox.Icon.Warning)

    def RemoveFromQueue(self):
        CurrentSelection = self.QueueTreeWidget.selectedItems()
        if len(CurrentSelection) > 0:
            CurrentFile = CurrentSelection[0]
            CurrentFileIndex = CurrentFile.Index
            if self.DisplayMessageBox("Remove this file from the queue?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)) == QMessageBox.StandardButton.Yes:
                self.Renamer.RemoveFileFromQueue(CurrentFileIndex)
                self.UpdateQueue()
                FileQueueLength = len(self.Renamer.FileQueue)
                if FileQueueLength > 0:
                    self.QueueTreeWidget.SelectIndex(CurrentFileIndex if CurrentFileIndex < FileQueueLength else FileQueueLength - 1)

    def MoveFileUp(self):
        self.MoveFile(-1)

    def MoveFileDown(self):
        self.MoveFile(1)

    def MoveFile(self, Delta):
        CurrentSelection = self.QueueTreeWidget.selectedItems()
        if len(CurrentSelection) > 0:
            CurrentFile = CurrentSelection[0]
            CurrentFileIndex = CurrentFile.Index
            if self.Renamer.MoveFileInQueue(CurrentFileIndex, Delta):
                self.UpdateQueue()
                self.QueueTreeWidget.SelectIndex(CurrentFileIndex + Delta)

    def ClearQueue(self):
        if self.DisplayMessageBox("Clear the file queue?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)) == QMessageBox.StandardButton.Yes:
            self.Renamer.ClearQueue()
            self.UpdateQueue()

    def ValidRenamePaths(self):
        for File in self.Renamer.GeneratedQueue:
            for Character in self.RestrictedCharacters:
                if Character in File["Generated Name"]:
                    return False
        return True

    def Rename(self):
        if not self.ValidRenamePaths():
            RestrictedCharactersString = ""
            for Character in self.RestrictedCharacters:
                RestrictedCharactersString += f"{Character} "
            RestrictedCharactersString.rstrip()
            self.DisplayMessageBox(f"Renamed files cannot contain the following characters:\n\n{RestrictedCharactersString}", Icon=QMessageBox.Icon.Warning)
            return

        # Start Renaming Thread
        self.SetRenameInProgress(True)
        self.Renamer.RenameFilesInQueue()

        # Attempt to Get Rename Thread and Set Up Status Checking
        try:
            RenameThreadInst = [RenameThread for RenameThread in threading.enumerate() if RenameThread.name == "RenameThread"][0]
            StatusThreadInst = StatusThread(RenameThreadInst)
            StatusThreadInst.UpdateProgressSignal.connect(lambda: self.UpdateProgress(RenameThreadInst))
            StatusThreadInst.RenameCompleteSignal.connect(self.RenameComplete)
            StatusThreadInst.start()
        except IndexError:
            self.RenameComplete()

    # Interface Methods
    def DisplayMessageBox(self, Message, Icon=QMessageBox.Icon.Information, Buttons=QMessageBox.StandardButton.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec()

    def UpdateQueue(self):
        self.AddToQueueButton.setEnabled(len(self.Renamer.FileQueue) == 0)
        self.Renamer.Prefix = self.PrefixLineEdit.text()
        self.Renamer.StartAt = self.NumberStartSpinBox.value()
        self.Renamer.Suffix = self.SuffixLineEdit.text()
        self.Renamer.Extension = self.ExtensionLineEdit.text()
        self.Renamer.ExtraDigits = self.ExtraDigitsSpinBox.value()
        self.QueueTreeWidget.FillFromQueue()

    def SetRenameInProgress(self, RenameInProgress):
        self.RenameInProgress = RenameInProgress
        for Widget in self.DisableList:
            Widget.setDisabled(RenameInProgress)
        if RenameInProgress:
            self.StatusBar.showMessage("Renaming in progress...")
        else:
            self.StatusBar.clearMessage()
            self.RenameProgressBar.reset()

    def UpdateProgress(self, RenameThread):
        RenameProgress = math.floor((RenameThread.FilesRenamed / RenameThread.FileQueueSize) * 100)
        self.RenameProgressBar.setValue(RenameProgress)

    def RenameComplete(self):
        self.SetRenameInProgress(False)
        self.Renamer.ClearQueue()
        self.UpdateQueue()

    # Window Management Methods
    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        DesktopCenterPoint = QApplication.primaryScreen().availableGeometry().center()
        FrameGeometryRectangle.moveCenter(DesktopCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())

    def CreateThemes(self):
        self.Themes = {}

        # Light
        self.Themes["Light"] = QPalette()
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(247, 247, 247, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, QColor(247, 247, 247, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(0, 120, 215, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(233, 231, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(227, 227, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, QColor(105, 105, 105, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(0, 120, 215, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(233, 231, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(227, 227, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, QColor(105, 105, 105, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))

        # Dark
        self.Themes["Dark"] = QPalette()
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(35, 38, 41, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(61, 174, 233, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(35, 38, 41, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(61, 174, 233, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))

    def LoadTheme(self):
        self.CreateThemes()
        ThemeFile = self.GetResourcePath("Configs/Theme.cfg")
        if os.path.isfile(ThemeFile):
            with open(ThemeFile, "r") as ConfigFile:
                self.Theme = json.loads(ConfigFile.read())
        else:
            self.Theme = "Light"
        self.AppInst.setStyle("Fusion")
        self.AppInst.setPalette(self.Themes[self.Theme])

    def SetTheme(self):
        Themes = list(self.Themes.keys())
        Themes.sort()
        CurrentThemeIndex = Themes.index(self.Theme)
        Theme, OK = QInputDialog.getItem(self, "Set Theme", "Set theme (requires restart to take effect):", Themes, current=CurrentThemeIndex, editable=False)
        if OK:
            self.Theme = Theme
            self.DisplayMessageBox(f"The new theme will be active after {self.ScriptName} is restarted.")

    # Close Event
    def closeEvent(self, Event):
        Close = True
        if self.RenameInProgress:
            Close = self.DisplayMessageBox("Files are currently being renamed.  Exit anyway?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)) == QMessageBox.StandardButton.Yes
        if Close:
            self.SaveConfigs()
            Event.accept()
        else:
            Event.ignore()
