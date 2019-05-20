# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

with open('README.rst') as file:
    readme = file.read()

with open("VERSION") as f:
    version = f.readline()
    f.close()
    
setup(
    name        =   'pydoas',
    version     =   version,
    author      =   'Jonas Gliss',
    author_email=   'jonasgliss@gmail.com',
    url         =   'https://github.com/jgliss/pydoas.git',
    license     =   'BSD3',
    package_dir =   {'pydoas'     :   'pydoas'},
    packages    =   find_packages(exclude=['contrib', 'docs', 'tests*']),
    #include_package_data = True,            
    package_data=   {'pydoas'     :   ['data/*.txt',
                                       'data/*/*.csv',
                                       'data/*/*.dat']
                    },
# =============================================================================
#                                         'data/doasis_resultfiles/*.csv',
#                                         'data/fake_resultfiles/*.csv']},
# 
# =============================================================================
#    data_files = [('scripts', ['scripts/*.py'])],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.,
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],

    install_requires    =   [],
    dependency_links    =   [],
    description = ("A Python toolbox for post analysis of DOAS "
                   "(Differential Optical Absorbtion Spectroscopy) results"),
    long_description = readme,
)