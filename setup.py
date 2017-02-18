# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

with open('README.rst') as file:
    readme = file.read()

with open("VERSION.rst") as f:
    version = f.readline()
    f.close()
    
setup(
    name        =   'pydoas',
    version     =   version,
    author      =   'Jonas Gliss',
    author_email=   'jg@nilu.no',
    url         =   'https://github.com/jgliss/pydoas.git',
    license     =   'BSD3',
    package_dir =   {'pydoas'     :   'pydoas'},
    packages    =   find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data = True,            
    package_data =   {'pydoas'          : ['data/*/*.dat', 
                                           'data/*/*.csv',
                                           'data/*.txt'],
                      'pydoas.scripts'   : ['scripts/*.py']},

#    data_files = [('scripts', ['scripts/*.py'])],
                  
    install_requires    =   ["numpy",
                             "pandas",
                             "sphinxcontrib-images"],
    dependency_links    =   [],
    description = ("A Python toolbox for post analysis of DOAS "
            "(Differential Optical Absorbtion Spectroscopy) results"),
    long_description = readme,
)