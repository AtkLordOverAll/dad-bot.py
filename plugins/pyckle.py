import os
import pickle

class Pyckle():

    """
    Allows for easier manipulation of pickles.
    If a pickle isn't found data will be None.
    """

    def __init__(self, fileName):
        if not fileName.endswith(".pickle"):
            fileName += ".pickle"
        if not os.path.isfile(fileName):
            data = None
            print("File not found, Pyckle blank")
        else:
            try:
                with open(fileName, "rb") as f:
                    data = pickle.load(f)
            except ValueError:
                data = None
                print("Data read failed, Pyckle blank")
        self.fileName = fileName
        self.data = data

    def save(self):
        with open(self.fileName, "wb") as f:
            pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)
