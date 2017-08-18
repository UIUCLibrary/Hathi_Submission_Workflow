from setuptools import setup
import os
import hsw

metadata_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hsw', '__version__.py')
metadata = dict()
with open(metadata_file, 'r', encoding='utf-8') as f:
    exec(f.read(), metadata)

with open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name=metadata["__title__"],
    version=metadata["__version__"],
    packages=['hsw'],
    url=metadata["__url__"],
    license='University of Illinois/NCSA Open Source License',
    author=metadata["__author__"],
    author_email=metadata["__author_email__"],
    description=metadata["__description__"],
    install_requires=["PyQt5"],
    long_description=readme,
    test_suite="tests",
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
         "console_scripts": [
             'hsw = hsw.__main__:main'
         ]
     },
)
