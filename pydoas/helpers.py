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
"""
Module containing all sorts of helper methods
"""

from datetime import datetime, time, date

def to_datetime(value):
    """Method to evaluate time and / or date input and convert to datetime"""
    if isinstance(value, datetime):
        return value
    elif isinstance(value, date):
        return datetime.combine(value, time())
    elif isinstance(value, time):
        return datetime.combine(date(1900,1,1), value)
    else:
        raise ValueError("Conversion into datetime object failed for input: "
            "%s (type: %s)" %(value, type(value)))       
    
