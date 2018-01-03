"""
    TODO:
        - encrypt whole file not just username and pwd
"""
import json
import base64
import os

class DataReader(object):

    def __init__(self):
        self.file_dir = os.getcwd()+"/data/datafile.json"
        self.data = {}
        self.load_file()

    def save_login(self, site, user, pwd):
        self.data['creds'][site]['username'] = self.encrypt(user).decode('utf-8')
        self.data['creds'][site]['pwd'] = self.encrypt(pwd).decode('utf-8')
        self.save_file()

    def load_login(self, site):
        self.load_file()
        usr = self.data['creds'][site]['username']
        pwd = self.data['creds'][site]['pwd']
        try:
            return tuple((self.decrypt(usr), self.decrypt(pwd)))
        except TypeError:
            return tuple(("", ""))

    def save_last_dir(self, last_dir):
        self.data['last_dir'] = last_dir
        self.save_file()

    def load_last_dir(self):
        self.load_file()
        return self.data['last_dir']

    def encrypt(self, pwd):
        pwd = bytes(pwd, 'utf-8')
        return base64.b64encode(pwd)

    def decrypt(self, pwd):
        return base64.b64decode(pwd).decode('utf-8')

    def load_file(self):
        with open(self.file_dir, 'r') as f:
            self.data = json.loads(f.read())

    def save_file(self):
        with open(self.file_dir, 'w') as f:
            json_string = json.dumps(self.data)
            f.write(json_string)

    def reset_data(self):
        self.data = {"last_dir": "", "creds": {"Lynda": {"username": None, "pwd": None}, "Skillshare¡": {"username": None, "pwd": None}, "Pluralsight": {"username": None, "pwd": None}, "Udemy": {"username": None, "pwd": None}}}
        self.save_file()
