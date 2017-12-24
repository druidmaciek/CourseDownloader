from setuptools import setup

APP = ['gui.py']
DATA_FILES = ['data']
OPTIONS = {
'argv_emulation': True,
           'site_packages': True,
           'iconfile': 'data/icon.icns',
           'plist': {
                'CFBundleName': 'Course Downloader',
                'CFBundleShortVersionString':'1.0.0', # must be in X.X.X format
                'CFBundleVersion': '1.0.0'}
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'], install_requires=[
        'validators', 'wxPython', 'selenium', 'bs4']
)
