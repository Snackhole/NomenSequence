import os


class Renamer:
    def __init__(self):
        # Variables
        self.FileQueue = []
        self.Prefix = ""
        self.StartAt = 0
        self.Suffix = ""
        self.Extension = ""
        self.GeneratedQueue = []

    def GenerateQueue(self):
        self.GeneratedQueue = []
        CurrentNumber = self.StartAt
        CountOfFiles = len(self.FileQueue)
        DigitsInCount = len(str(CountOfFiles))
        for File in self.FileQueue:
            GeneratedNamePair = {}
            GeneratedNamePair["Original Name"] = File
            FileNumberString = str(CurrentNumber)
            if len(FileNumberString) < DigitsInCount:
                FileNumberString = ("0" * (DigitsInCount - len(FileNumberString))) + FileNumberString
            GeneratedNamePair["Rename To"] = os.path.join(os.path.dirname(File), self.Prefix + FileNumberString + self.Suffix + self.Extension)
            CurrentNumber += 1
        return self.GeneratedQueue
