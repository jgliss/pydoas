# -*- coding: utf-8 -*-
from pkg_resources import get_distribution

__version__ = get_distribution('pydoas').version

from os.path import abspath, dirname

_LIBDIR = abspath(dirname(__file__))

from .inout import *  #from .io import get_data_dirs, get_data_files
import helpers
from dataimport import ResultImportSetup
from analysis import DatasetDoasResults, DoasResults

