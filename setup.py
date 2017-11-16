from setuptools import setup
from setuptools.command.build_py import build_py
import os


class BuildPyCommand(build_py):
    def run(self):
        from PyQt5 import uic
        print("Building Gui")
        building_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(building_path, "hsw", "ui", "ui_packages.py"), "w") as ui_writer:
            uic.compileUi(uifile=os.path.join(building_path, "ui", "ui_packages.ui"), pyfile=ui_writer)
        build_py.run(self)


setup(

    packages=['hsw', "hsw.ui"],
    install_requires=[
        "pyqt5",
        "pyhathiprep >= 0.1.3",
        "HathiValidate",
        "imgvalidator",
        "HathiZip"
    ],
    test_suite="tests",
    setup_requires=[
        "pytest-runner",
        "pyqt5"
    ],
    cmdclass={
        "build_py": BuildPyCommand
    },
    tests_require=['pytest'],
    entry_points={
        "gui_scripts": [
            'hsw = hsw.__main__:main'
        ]
    },
)
