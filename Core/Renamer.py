import os
import queue
import threading


class Renamer:
    def __init__(self):
        # Variables
        self.FileQueue = []
        self.Prefix = ""
        self.StartAt = 1
        self.ExtraDigits = 0
        self.Suffix = ""
        self.Extension = ""
        self.GeneratedQueue = []

    def GenerateQueue(self):
        self.GeneratedQueue = []
        CurrentNumber = self.StartAt
        CountOfFiles = len(self.FileQueue)
        DigitsInCount = len(str(CountOfFiles + self.StartAt - 1)) + self.ExtraDigits
        for File in self.FileQueue:
            GeneratedNamePair = {}
            GeneratedNamePair["Original Name"] = File
            FileNumberString = str(CurrentNumber)
            if len(FileNumberString) < DigitsInCount:
                FileNumberString = f"{"0" * (DigitsInCount - len(FileNumberString))}{FileNumberString}"
            GeneratedNamePair["Rename To"] = os.path.join(os.path.dirname(File), f"{self.Prefix}{FileNumberString}{self.Suffix}{self.Extension}")
            CollisionSuffix = 1
            while os.path.isfile(GeneratedNamePair["Rename To"]):
                GeneratedNamePair["Rename To"] = f"{os.path.splitext(GeneratedNamePair["Rename To"])[0]}-{str(CollisionSuffix)}{self.Extension}"
                CollisionSuffix += 1
            self.GeneratedQueue.append(GeneratedNamePair)
            CurrentNumber += 1
        return self.GeneratedQueue

    def AddFileToQueue(self, File):
        if File in self.FileQueue:
            return False
        self.FileQueue.append(File)
        return True

    def AddFilesToQueue(self, Files):
        AllFilesAdded = True
        for File in Files:
            AllFilesAdded = self.AddFileToQueue(File) and AllFilesAdded
        return AllFilesAdded

    def RemoveFileFromQueue(self, FileIndex):
        del self.FileQueue[FileIndex]

    def MoveFileInQueue(self, FileIndex, Delta):
        TargetIndex = FileIndex + Delta
        if TargetIndex < 0 or TargetIndex >= len(self.FileQueue):
            return False
        SwapTarget = self.FileQueue[TargetIndex]
        self.FileQueue[TargetIndex] = self.FileQueue[FileIndex]
        self.FileQueue[FileIndex] = SwapTarget
        return True

    def MoveFileUpInQueue(self, FileIndex):
        return self.MoveFileInQueue(FileIndex, -1)

    def MoveFileDownInQueue(self, FileIndex):
        return self.MoveFileInQueue(FileIndex, 1)

    def ClearQueue(self):
        self.FileQueue.clear()
        self.GeneratedQueue.clear()

    def RenameFilesInQueue(self):
        class RenameThread(threading.Thread):
            def __init__(self, FileQueue):
                # Store Parameters
                self.FileQueue = FileQueue

                # Variables
                self.RenameComplete = False
                self.FilesRenamed = 0
                self.FileQueueSize = self.FileQueue.qsize()

                # Initialize
                super().__init__(name="RenameThread", daemon=True)

            def run(self):
                while not self.FileQueue.empty():
                    QueuedFile = self.FileQueue.get()
                    os.rename(QueuedFile["Original Name"], QueuedFile["Rename To"])
                    self.FilesRenamed += 1
                self.RenameComplete = True

        FileQueue = queue.Queue()
        for QueuedFile in self.GeneratedQueue:
            FileQueue.put(QueuedFile)

        RenameThreadInst = RenameThread(FileQueue)
        RenameThreadInst.start()
