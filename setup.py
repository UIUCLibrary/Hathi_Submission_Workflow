from setuptools import setup
# from dis
from setuptools.command.build_py import build_py
# from distutils.command.build import build
import os
import hsw


class BuildPyCommand(build_py):
    def run(self):
        from PyQt5 import uic
        print("Building Gui")
        building_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(building_path, "hsw", "ui", "ui_packages.py"), "w") as ui_writer:
            uic.compileUi(uifile=os.path.join(building_path, "ui", "ui_packages.ui"), pyfile=ui_writer)
        build_py.run(self)


metadata_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hsw', '__version__.py')
metadata = dict()
with open(metadata_file, 'r', encoding='utf-8') as f:
    exec(f.read(), metadata)

with open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name=metadata["__title__"],
    version=metadata["__version__"],
    packages=['hsw', "hsw.ui"],
    url=metadata["__url__"],
    license='University of Illinois/NCSA Open Source License',
    author=metadata["__author__"],
    author_email=metadata["__author_email__"],
    description=metadata["__description__"],
    install_requires=[
        "pyqt5",
        "pyhathiprep >= 0.1.3",
        "HathiValidate",
        "imgvalidator",
        "HathiZip"
    ],
    long_description=readme,
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
