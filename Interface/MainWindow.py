import os

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QFrame, QGridLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton, QSpinBox

from Core.Renamer import Renamer
from Interface.Widgets.IconButtons import AddButton, DeleteButton, MoveDownButton, MoveUpButton
from Interface.Widgets.QueueTreeWidget import QueueTreeWidget


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath

        # Variables
        self.RenameInProgress = False

        # Initialize
        super().__init__()

        # Create Renamer
        self.Renamer = Renamer()

        # Create Interface
        self.CreateInterface()

        # Show Window
        self.show()

        # Center Window
        self.Center()

        # Load Configs
        self.LoadConfigs()

        # Update Queue
        self.UpdateQueue()

    def CreateInterface(self):
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
        self.InputSeparator = QFrame()
        self.InputSeparator.setFrameShape(QFrame.HLine)
        self.InputSeparator.setFrameShadow(QFrame.Sunken)
        self.PrefixLineEdit = QLineEdit()
        self.PrefixLineEdit.setPlaceholderText("Prefix")
        self.PrefixLineEdit.textChanged.connect(self.UpdateQueue)
        self.NumberStartSpinBox = QSpinBox()
        self.NumberStartSpinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.NumberStartSpinBox.setButtonSymbols(self.NumberStartSpinBox.NoButtons)
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
        self.ExtraDigitsSpinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.ExtraDigitsSpinBox.setButtonSymbols(self.ExtraDigitsSpinBox.NoButtons)
        self.ExtraDigitsSpinBox.setRange(0, 1000000000)
        self.ExtraDigitsSpinBox.setPrefix("Extra digits:  ")
        self.ExtraDigitsSpinBox.setValue(0)
        self.ExtraDigitsSpinBox.valueChanged.connect(self.UpdateQueue)
        self.RenameButton = QPushButton("Rename Files")
        self.RenameButton.clicked.connect(self.Rename)
        self.ProgressSeparator = QFrame()
        self.ProgressSeparator.setFrameShape(QFrame.HLine)
        self.ProgressSeparator.setFrameShadow(QFrame.Sunken)
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
        # self.Layout.addWidget(self.InputSeparator, 2, 0, 1, 5)
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

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

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

    def SaveConfigs(self):
        if not os.path.isdir(self.GetResourcePath("Configs")):
            os.mkdir(self.GetResourcePath("Configs"))

        # Last Opened Directory
        if type(self.LastOpenedDirectory) == str:
            if os.path.isdir(self.LastOpenedDirectory):
                with open(self.GetResourcePath("Configs/LastOpenedDirectory.cfg"), "w") as ConfigFile:
                    ConfigFile.write(self.LastOpenedDirectory)

    def AddToQueue(self):
        FilesToAdd = QFileDialog.getOpenFileNames(caption="Files to Add to Queue", directory=self.LastOpenedDirectory)[0]
        if len(FilesToAdd) < 1:
            return
        AllFilesAddedSuccessfully = self.Renamer.AddFilesToQueue(FilesToAdd)
        self.UpdateQueue()
        self.LastOpenedDirectory = os.path.dirname(FilesToAdd[0])
        if not AllFilesAddedSuccessfully:
            self.DisplayMessageBox("Some of the selected files could not be added to the queue.  They may have already been in the queue.", Icon=QMessageBox.Warning)

    def RemoveFromQueue(self):
        CurrentSelection = self.QueueTreeWidget.selectedItems()
        if len(CurrentSelection) > 0:
            CurrentFile = CurrentSelection[0]
            CurrentFileIndex = CurrentFile.Index
            if self.DisplayMessageBox("Remove this file from the queue?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.Yes:
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
        if self.DisplayMessageBox("Clear the file queue?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.Yes:
            self.Renamer.ClearQueue()
            self.UpdateQueue()

    def Rename(self):
        pass

    def DisplayMessageBox(self, Message, Icon=QMessageBox.Information, Buttons=QMessageBox.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec_()

    def UpdateQueue(self):
        self.AddToQueueButton.setEnabled(len(self.Renamer.FileQueue) == 0)
        self.Renamer.Prefix = self.PrefixLineEdit.text()
        self.Renamer.StartAt = self.NumberStartSpinBox.value()
        self.Renamer.Suffix = self.SuffixLineEdit.text()
        self.Renamer.Extension = self.ExtensionLineEdit.text()
        self.Renamer.ExtraDigits = self.ExtraDigitsSpinBox.value()
        self.QueueTreeWidget.FillFromQueue()

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
