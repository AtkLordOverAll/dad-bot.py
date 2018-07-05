import os
import json


class Pyson:

    """
    Allows for easier manipulatoin of JSON files.
    It will check if a .json file already exists with the given file name and open that, otherwise it will create a new one.
    """

    def __init__(self, fileName):
        if not fileName.endswith('.json'):
            fileName = fileName + '.json'
        if not os.path.isfile(fileName):
            data = {}
        else:
            try:
                with open(fileName) as f:
                    data = json.load(f)
            except ValueError:
                print("Data read failed, using blank dict.")
                data = {}
        self.fileName = fileName
        self.data = data

    def save(self, sort = False):
        with open(self.fileName, "w") as f:
            json.dump(self.data, f, indent=4, sort_keys=sort)
