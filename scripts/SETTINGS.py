# -*- coding: utf-8 -*-
#
# Pyplis is a Python library for the analysis of UV SO2 camera data
# Copyright (C) 2017 Jonas Gliß (jonasgliss@gmail.com)
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License a
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import argparse
import pathlib
from matplotlib import rcParams


rcParams.update({'figure.autolayout': True})
rcParams.update({'font.size': 13})

# if True, some of the actual results of the scripts are verified
TESTMODE = True

SAVEFIGS = 1 # save plots from this script in SAVE_DIR
DPI = 150 #pixel resolution for saving
FORMAT = "png" #format for saving

SCREENPRINT = 0 #show images on screen when executing script

# Directory where results are stored
# Directory where results are stored
SCRIPTS_DIR = pathlib.Path(__file__).parent
SAVE_DIR = SCRIPTS_DIR / "scripts_out"

ARGPARSER = argparse.ArgumentParser()
ARGPARSER.add_argument('--show', default=SCREENPRINT)
ARGPARSER.add_argument('--test', default=TESTMODE)