from setuptools import setup

APP = ['test26.py']  # your script name
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': None,
    'packages': ['rumps', 'requests'],
    'includes': ['rumps', 'requests'],
    'plist': {
        'CFBundleName': 'WiFi Monitor',
        'CFBundleDisplayName': 'WiFi Monitor',
        'CFBundleIdentifier': 'com.wleed.wifimonitor',
        'CFBundleVersion': '1.0.0',
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

