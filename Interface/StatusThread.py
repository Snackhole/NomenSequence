import threading
from PyQt5 import QtCore


class StatusThread(QtCore.QObject):
    UpdateProgressSignal = QtCore.pyqtSignal()
    RenameCompleteSignal = QtCore.pyqtSignal()

    def __init__(self, RenameThread):
        super().__init__()
        self.RenameThread = RenameThread
        self.Thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.Thread.start()

    def run(self):
        while not self.RenameThread.RenameComplete:
            self.UpdateProgressSignal.emit()
        self.RenameCompleteSignal.emit()
