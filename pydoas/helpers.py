# -*- coding: utf-8 -*-
"""
Module containing all sorts of helper methods
"""

import matplotlib.cm as colormaps
import matplotlib.colors as colors
from datetime import datetime, time, date

from matplotlib.pyplot import draw
from numpy import linspace, hstack, vectorize, int, floor, log10, isnan

exponent = lambda num: int(floor(log10(abs(num))))

time_delta_to_seconds = vectorize(lambda x: x.total_seconds())

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
        
def isnum(val):
    """Checks if input is number (int or float) and not nan
    
    :returns: bool, True or False    
    """
    if isinstance(val, (int, float)) and not isnan(val):
        return True
    return False

def shifted_color_map(vmin, vmax, cmap = None):
    """Shift center of a diverging colormap to value 0
    
    .. note::
    
        This method was found `here <http://stackoverflow.com/questions/
        7404116/defining-the-midpoint-of-a-colormap-in-matplotlib>`_ 
        (last access: 17/01/2017). Thanks to `Paul H <http://stackoverflow.com/
        users/1552748/paul-h>`_ who provided it.
    
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and if you want the
    middle of the colormap's dynamic range to be at zero level
    
    :param vmin: lower end of data value range
    :param vmax: upper end of data value range
    :param cmap: colormap (if None, use default cmap: seismic)
    
    :return: 
        - shifted colormap
        
    """

    if cmap is None:
        cmap = colormaps.seismic
        
    midpoint = 1 - abs(vmax)/(abs(vmax) + abs(vmin))
    
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = linspace(0, 1, 257)

    # shifted index to match the data
    shift_index = hstack([
        linspace(0.0, midpoint, 128, endpoint=False), 
        linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    return colors.LinearSegmentedColormap('shiftedcmap', cdict)
    
def _print_list(lst):
    """Print a list rowwise"""
    for item in lst:
        print item

def rotate_xtick_labels(ax, deg=30, ha="right"):
    """Rotate xtick labels in matplotlib axes object"""
    draw()
    lbls = ax.get_xticklabels()
    lbls = [lbl.get_text() for lbl in lbls]
    ax.set_xticklabels(lbls, rotation = 30, ha = "right")
    draw()
    return ax
    
