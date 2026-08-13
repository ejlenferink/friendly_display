from setuptools import setup, find_packages
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
import sys
sys.path.insert(1, os.path.join(dir_path, 'friendly_display'))
from __version__ import __version__

def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

setup(
    name = 'friendly_display',
    version = __version__,
    packages = find_packages(include=['friendly_display']),
    package_data = {
        'friendly_display': [
            '*.json', 
        ]
    },
    include_package_data = True,
    install_requires = read_requirements()
)
