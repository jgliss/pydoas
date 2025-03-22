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
def get_pydoas_version():
    import pathlib
    pkg_root = pathlib.Path(__file__).parent.parent
    with open(pkg_root / "VERSION") as f:
        version = f.readline()
    return version

__version__ = get_pydoas_version()

from os.path import abspath, dirname

_LIBDIR = abspath(dirname(__file__))

from .inout import *
from . import helpers
from .dataimport import ResultImportSetup
from .analysis import DatasetDoasResults, DoasResults

