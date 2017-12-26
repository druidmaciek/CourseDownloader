import json


class DataReader(object):

    def __init__(self):
        self.data = self.load_file()

    def save_password(self, site):
        pass

    def load_password(self, site):
        pass

    def save_last_dir(self):
        pass

    def load_last_dir(self):
        pass

    def encrypt(self):
        pass

    def decrypt(self):
        pass

    def load_file(self):
        with open('datafile.json', 'r') as f:
            return json.loads(f.read())

    def save_file(self):
        with open('datafile.json', 'w') as f:
            json_string  = json.dumps(self.data)
            f.write(json_string)
