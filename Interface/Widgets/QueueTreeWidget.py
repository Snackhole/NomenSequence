import os

from PyQt5.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem


class QueueTreeWidget(QTreeWidget):
    def __init__(self, MainWindow):
        super().__init__()

        # Store Parameters
        self.MainWindow = MainWindow

        # Header Setup
        self.setRootIsDecorated(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setColumnCount(3)
        self.setHeaderLabels(["Original Name", "", "Renamed To..."])

    def FillFromQueue(self):
        self.clear()
        GeneratedQueue = self.MainWindow.Renamer.GenerateQueue()
        for FileIndex in range(len(GeneratedQueue)):
            self.invisibleRootItem().addChild(QueueTreeWidgetItem(self.MainWindow, FileIndex, GeneratedQueue[FileIndex]))

    def SelectIndex(self, Index):
        DestinationIndex = self.model().index(Index, 0)
        self.setCurrentIndex(DestinationIndex)
        self.scrollToItem(self.currentItem(), self.PositionAtCenter)
        self.horizontalScrollBar().setValue(0)


class QueueTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, MainWindow, Index, File):
        super().__init__()

        # Store Parameters
        self.MainWindow = MainWindow
        self.Index = Index
        self.File = File

        # Variables
        self.OriginalNameText = os.path.basename(self.File["Original Name"])
        self.SeparatorText = " -> "
        self.RenameToText = os.path.basename(self.File["Rename To"])
        self.ColumnTextList = [self.OriginalNameText, self.SeparatorText, self.RenameToText]

        # Set Text
        for Column in range(len(self.ColumnTextList)):
            self.setText(Column, self.ColumnTextList[Column])
            self.setToolTip(Column, self.ColumnTextList[Column])
