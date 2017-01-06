# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

with open('README.rst') as file:
    readme = file.read()
    
setup(
    name        =   'pydoas',
    version     =   '1.0.0',
    author      =   'Jonas Gliss',
    author_email=   'jg@nilu.no',
    license     =   'BSD3',
    package_dir =   {'pydoas'     :   'pydoas'},
    packages    =   find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data = True,            
    package_data =   {'pydoas'          : ['data/*/*.dat', 'data/*.txt'],
                      'pydoas.scripts'   : ['scripts/*.py']},

#    data_files = [('scripts', ['scripts/*.py'])],
                  
    install_requires    =   ["numpy",
                             "pandas"],
    dependency_links    =   [],
    description = ("A Python toolbox for the analysis of DOAS (Differential"
            "Optical Absorbtion Spectroscopy) results"),
    long_description = readme,
)