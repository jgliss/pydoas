# -*- coding: utf-8 -*-
"""
This module contains I/O routines for DOAS result files
"""
from os.path import join
from os import listdir

def get_data_dirs():
    """Get directories containing example package data
    
    :returns: list of package subfolders containing data files
    """
    from pydoas import _LIBDIR    
    return listdir(join(_LIBDIR, "data"))
    
def get_data_files():
    """Get all example result files from package data"""
    from pydoas import _LIBDIR
    p = join(_LIBDIR, join("data", "doasis_resultfiles"))
    return listdir(p), p
    
def get_import_info(resulttype = "doasis"):
    """Try to load DOAS result import specification for default type 
    
    Import specifications for a specified data type (see package data
    file "import_info.txt" for available types, use the instructions in this
    file to create your own import setup if necessary)
    
    :param str resulttype: name of result type (field "type" in 
        "import_info.txt" file)
    
    """
    try:
        from pydoas import _LIBDIR
    except:
        raise
    dat = {}
    with open(join(_LIBDIR, join("data", "import_info.txt"))) as f:
        found = 0
        for line in f: 
            if "ENDTYPE" in line and found:
                return dat
            spl = line.split(":", 1)
            if found:
                if not any([line[0] == x for x in["#","\n"]]):
                    k = spl[0].strip()
                    d = [x.strip() for x in spl[1].split("#")[0].split(',')]
                    if len(d) > 1:
                        dat[k] = d
                    elif k == "delim":
                        dat[k] = str(d[0].decode("unicode_escape"))
                    else:
                        dat[k] = d[0]
            if spl[0] == "type" and spl[1].split("#")[0].strip() == resulttype:
                    found = 1    
    raise IOError("Info for type %s could not be found" %resulttype)

