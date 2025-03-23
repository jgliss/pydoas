# -*- coding: utf-8 -*-
#
# Pydoas is a Python library for the post-analysis of DOAS result data
# Copyright (C) 2017 Jonas Gliß (jonasgliss@gmail.com)
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the BSD 3-Clause License
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See BSD 3-Clause License for more details 
# (https://opensource.org/licenses/BSD-3-Clause)
from importlib import metadata
__version__ = metadata.version("pydoas")

from os.path import abspath, dirname

_LIBDIR = abspath(dirname(__file__))

from .inout import *
from . import helpers
from .dataimport import ResultImportSetup
from .analysis import DatasetDoasResults, DoasResults

