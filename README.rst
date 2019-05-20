pydoas is a Python library for reading, postprocessing and plotting of DOAS (Differential Optical Absorption Spectroscopy) fit results. 
It supports default import of the result file format of
`DOASIS <https://doasis.iup.uni-heidelberg.de/bugtracker/projects/doasis/>`_. Further import formats for fast data access can easily be defined by the user.

News
====

18 Feb 2018: now also supports Python3

Copyright
=========

Copyright (C) 2017 Jonas Gliss (jonasgliss@gmail.com)

This program is free software: you can redistribute it and/or modify it under the terms of the BSD 3-Clause License

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See BSD 3-Clause License for more details (https://opensource.org/licenses/BSD-3-Clause)

Requirements
============

- numpy
- matplotlib
- pandas

Installation
============

First, make sure to have all requirements installed (prev. section). Then, pydoas can be installed from `PyPi <https://pypi.python.org/pypi/pydoas>`__ using::

  pip install pydoas
  
or from source (hosted on GitHub) by `downloading and extracting the latest release <https://github.com/jgliss/pydoas>`_ or downloading / cloning the repo. If you download manually, call::

  python setup.py install
  
after download and extraction of the source directory.
  
Instructions and code documentation
===================================

The code documentation of pydoas is hosted `here <http://pydoas.readthedocs.io/en/latest/index.html>`_

Getting started
===============

After installation try running the `example scripts <http://pydoas.readthedocs.io/en/latest/examples.html>`_ in order to test the installation. The scripts are also meant to provide an easy start into the main features of pydoas.
