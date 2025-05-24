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

from datetime import datetime, timedelta, date
from typing import Optional, Sequence
from numpy import asarray, full, polyfit, poly1d, logical_and, polyval, ndarray
from pandas import Series, DataFrame
from matplotlib.pyplot import subplots
from matplotlib.dates import DateFormatter

from pydoas.helpers import to_datetime
from pydoas.dataimport import DataImport, ResultImportSetup
            
class DatasetDoasResults(object):
    """A Dataset for DOAS fit results import and processing
    
    Attributes:
        setup (ResultImportSetup): setup specifying all necessary import 
            settings (please see documentation of :class:`ResultImportSetup`
            for setup details)
        raw_results (dict): dictionary containing the imported results

    Args:
        setup (ResultImportSetup): setup specifying all necessary import 
            settings (please see documentation of :class:`ResultImportSetup`
            for setup details)
        init (int): if 1, the raw results will be loaded immediately
        **kwargs: alternative way to setup :attr:`setup` 
            (:class:`ResultImportSetup` object), which is only used in case
            input parameter **setup** is None.

    """
    def __init__(self, setup: ResultImportSetup = None, init: bool = 1, **kwargs):
        
        self.setup = None
        self.raw_results = {}
        
        self.load_input(setup, **kwargs)
        if init:
            self.load_raw_results()
            
    def load_input(self, setup: ResultImportSetup = None, **kwargs):
        """Process input information
        
        Args:
            setup (ResultImportSetup): setup specifying all necessary import 
                settings (please see documentation of :class:`ResultImportSetup`
                for setup details)
            **kwargs: alternative way to setup :attr:`setup` 
                (:class:`ResultImportSetup` object), which is only used in case
                input parameter **setup** is None.   

        """
        if not isinstance(setup, ResultImportSetup):
            setup = ResultImportSetup(**kwargs)
        self.setup = setup
    
    @property
    def base_path(self) -> str:
        """Basepath of resultfiles"""
        return self.setup.base_path
        
    @property
    def start(self) -> datetime:
        """Start date and time of dataset"""
        return self.setup.start
        
    @property
    def stop(self) -> datetime:
        """Stop date and time of dataset"""
        return self.setup.stop
    
    @property
    def dev_id(self) -> str:
        """Device ID of dataset"""
        return self.setup.dev_id
    
    @property
    def import_info(self):
        """Returns information about result import details"""
        return self.setup.import_info
        
    def change_time_ival(self, start: datetime, stop: datetime) -> None:
        """Change the time interval for the considered dataset
        
        Note: 
            Previously loaded results will be deleted

        Args:
            start (datetime): new start time
            stop (datetime): new stop time    
        """
        if isinstance(start, datetime):
            self.start = start
        if isinstance(stop, datetime):
            self.stop = stop
        self.raw_results = {}
        
    def load_raw_results(self) -> bool:
        """Try to load all results as specified in the setup

        This method will try to load all results as specified in the setup. If
        the import setup is not complete, an exception will be raised.
        
        Returns:
            bool: True if data is loaded, False otherwise

        Raises:
            AttributeError: If the import setup is not complete
        """
        if not self.setup.complete():
            raise AttributeError("Import setup is not complete")
        access = DataImport(self.setup)
        if access.data_loaded:
            self.raw_results = access.results
            self.set_start_stop_time()
            return True
        return False
    
    def has_data(self, fit_id: str, species_id: str, start: datetime = None, stop: datetime = None) -> bool:
        """Checks if specific data is available
        
        Args:
            fit_id (str): ID of the fit scenario
            species_id (str): ID of the species
            start (datetime, optional): Start datetime for the data check
            stop (datetime, optional): Stop datetime for the data check
        
        Returns:
            bool: True if data is available, False otherwise
        """
        if not (fit_id in self.raw_results and species_id in self.raw_results[fit_id]):
            return False
        if all([isinstance(x, datetime) for x in [start, stop]]):
            ts = self.raw_results[fit_id]["start"]
            if not any([start < x < stop for x in ts]):
                return False
        return True
    
    def get_spec_times(self, fit: str) -> tuple:
        """Returns start time and stop time arrays for spectra to a given fit
        
        Args:
            fit (str): ID of the fit scenario
        
        Returns:
            tuple: start and stop time arrays for the spectra
        """

        start = asarray(self.raw_results[fit]["start"])
        stop = asarray(self.raw_results[fit]["stop"])
        return start, stop
           
            
    def set_start_stop_time(self):
        """Get start/stop range of dataset"""
        start_acq, stop_acq = [], []
        
        for fit_id in self.raw_results:
            ts, _ = self.get_spec_times(fit_id)
            if len(ts) > 0:
                start_acq.append(ts.min())
                stop_acq.append(ts.max())
        
        self.setup.start = min(start_acq)
        self.setup.stop = max(stop_acq)
        return self.start, self.stop
    
    def get_start_stop_mask(self, fit, start=None, stop=None):
        """Creates boolean mask for data access only in a certain time interval
        """
        if start is None:
            start = self.start
        elif isinstance(start, date): 
            #assume that all spectra from that day are supposed to be imported
            print ("Start time is date, loading results from all spectra of "
                    "that day")
            start = to_datetime(start)
            stop = start + timedelta(days=1)
        if stop is None:
            stop = self.stop
        i, f = self.get_spec_times(fit)
        mask = logical_and(i >= start, i <= stop)
        return mask, i[mask], f[mask]
        
    def get_meta_info(self, fit, meta_id, start=None, stop=None):
        """Get meta info array
        
        :param str meta_id: string ID of meta information
        :param array boolMask: boolean mask for data retrieval
        
        .. note::
        
            Bool mask must have same length as the meta data array
            
        """
        if meta_id not in self.raw_results[fit]:
            return 0
        m, start, stop = self.get_start_stop_mask(fit, start, stop)
        return Series(self.raw_results[fit][meta_id][m], start)
        
    def _get_data(self, species_id, fit_id):
        """Access raw data array
        
        :param str species_id: string ID of species
        :param str fit_id: string ID of fit scenario
    
        """
        return self.raw_results[fit_id][species_id]
        
    def get_results(self, species_id, fit_id=None, start=None, stop=None):
        """Get spectral results object
        
        :param str species_id: string ID of species
        :param str fit_id: string ID of fit scenario (if None, tries to 
            load default fit_id)
        :param start: if valid (i.e. datetime object) only data after that time
            stamp is considered
        :param stop: if valid (i.e. datetime object) only data before that time
            stamp is considered    
        """
        if fit_id is None:
            fit_id = self.setup.default_fit_ids[species_id]
        if not fit_id in self.setup.get_fit_ids():
            return False
        m, start, stop = self.get_start_stop_mask(fit_id, start, stop)
        if not sum(m):
            return False
        dat = self._get_data(species_id, fit_id)[m]
        times = start + (stop - start) / 2
        dat_err = self._get_data((species_id + "_err"), fit_id)[m]
        return DoasResults(dat, times, start, stop, dat_err, species_id, fit_id, 3)

    def get_default_fit_id(self, species_id):
        """Get default fit scenario id for species
        
        :param str species_id: ID of species (e.g. "so2")
        """
        return self.setup.default_fit_ids[species_id]
            
    def set_default_fitscenarios(self, default_dict):
        """Update default fit scenarios for species
        
        :param dict default_dict: dictionary specifying new default fit 
            scenarios, it could e.g. look like::
            
                default_dict = {"so2"   :   "f01",
                                "o3"    :   "f01",
                                "bro"   :   "f03"}
                                
        """
        try:
            self.setup.set_defaults(default_dict)
            return 1
        except:
            return 0
       
    def plot(self,species_id, fit_id=None, start=None, stop=None, **kwargs):
        """Plot DOAS results"""
        res = self.get_results(species_id, fit_id, start, stop)
        if res is not False:
            return res.plot(**kwargs)
        return 0
            
    def scatter_plot(self, species_id_xaxis, fit_id_xaxis, species_id_yaxis,
                     fit_id_yaxis, lin_fit_opt=1, species_id_zaxis=None, 
                     fit_id_zaxis=None, start=None, stop=None, ax=None, 
                     **kwargs):
        """Make a scatter plot of two species
        
        :param str species_id_xaxis: string ID of x axis species (e.g. "so2")
        :param str fit_id_xaxis: fit scenario ID of x axis species (e.g. "f01")
        :param str species_id_yaxis: string ID of y axis species (e.g. "so2")
        :param str fit_id_yaxis: fit scenario ID of y axis species (e.g. "f02")
        :param str species_id_zaxis: string ID of z axis species (e.g. "o3")
        :param str fit_id_zaxis: fit scenario ID of z axis species (e.g. "f01")
        :param datetime start: start time stamp for data retrieval
        :param datetime stop: stop time stamp for data retrieval
        :param ax: matplotlib axes object (None), if provided, then the result 
            is plotted into the axes
        :param kwargs: keyword arguments for matplotlib scatter plot
            (e.g. color, marker, edgecolor, etc.)
        """
        res_x = self.get_results(species_id_xaxis, fit_id_xaxis, start, stop)
        res_y = self.get_results(species_id_yaxis, fit_id_yaxis, start, stop)
        
        res_z = None
        if species_id_zaxis is not None and fit_id_zaxis is not None:
            res_z = self.get_results(\
                        species_id_zaxis, fit_id_zaxis, start, stop)
        if ax is None:
            fig, ax = subplots(1, 1)
        else:
            fig = ax.figure.canvas.figure
        if res_z is not None:
            sc = ax.scatter(res_x.values, res_y.values, 15, res_z.values,\
                                marker = 'o', edgecolor = 'none', **kwargs)
            cb = fig.colorbar(sc, ax = ax, shrink = 0.9, **kwargs)    
            cb.set_label(species_id_zaxis + " " + fit_id_zaxis, **kwargs)
        else:
            ax.plot(res_x.values, res_y.values, " b*", label = "Data",\
                                                                **kwargs)
        ax.set_xlabel(species_id_xaxis + " " + fit_id_xaxis)
        ax.set_ylabel(species_id_yaxis + " " + fit_id_yaxis)
        ax.grid()
        if lin_fit_opt:
            self.linear_regression(res_x.values, res_y.values, ax = ax)
        ax.legend(loc = 'best', fancybox = True, framealpha = 0.5, fontsize = 12)
        return ax 
    
    def linear_regression(self, x_data, y_data, mask = None, ax = None):
        """Perform linear regression and return parameters
        
        :param ndarray x_data: x data array
        :param ndarray y_data: y data array
        :param ndarray mask: mask specifying indices of input data supposed to 
            be considered for regression (None)
        :param ax: matplotlib axes object (None), if provided, then the result 
            is plotted into the axes
        """
        if mask is None:
            mask = full(len(y_data), True, dtype=bool)
        poly = poly1d(polyfit(x_data[mask], y_data[mask], 1))

        if ax is not None:
            ax.plot(x_data, polyval(poly, x_data), "--r",\
                                label = "Slope: %.2f" %(poly[1]))
        return poly
    
    def get_fit_import_setup(self):
        """Get the current fit import setup"""
        return self.setup.import_info

    def __getitem__(self, key):
        """Get attribute using bracketed syntax"""
        for k,v in list(self.__dict__.items()):
            if k == key:
                return v
            try:
                return v[key]
            except:
                pass

    def __setitem__(self, key, val):
        """Change attribute value using bracket syntax"""
        for k,v in list(self.__dict__.items()):
            if k == key:
                self.__dict__[key] = val
                return               
       
    def __str__(self):
        """String representation"""
        return ("\nDOAS result dataset\n-------------------\n" + str(self.setup))

class DoasResults(Series):
    """Data time series for handling and analysing DOAS fit results
    
    :param arraylike data: DOAS fit results (column densities)
    :param arraylike index: Time stamps of data points
    :param arraylike fit_errs: DOAS fit errors
    :param string species_id: String specifying the fitted species
    :param string fit_id: Unique string specifying the fit scenario used
    :param int fit_errs_corr_fac: DOAS fit error correction factor 
    """
    def __init__(
            self, 
            data: Sequence | ndarray | Series, 
            index: Optional[Sequence | ndarray] = None, 
            start_acq: Optional[Sequence | ndarray] = None, 
            stop_acq: Optional[Sequence | ndarray] = None,
            fit_errs: Optional[Sequence | ndarray] = None, 
            species_id: Optional[str] = None, 
            fit_id: Optional[str] = None,
            fit_errs_corr_fac=1.0):
        if start_acq is None:
            start_acq = []
        if stop_acq is None:
            stop_acq = []
        if species_id is None:
            species_id = ""
        if fit_id is None:
            fit_id = ""
        if isinstance(data, Series):
            index = data.index
            species_id = data.name
            data = data.values
        super().__init__(data, index, name=species_id)
        if fit_errs is None:
            fit_errs = []
            
        self.fit_errs = fit_errs

        self.fit_id = fit_id        
        self.fit_errs_corr_fac = fit_errs_corr_fac
        self.start_acq = start_acq
        self.stop_acq = stop_acq
         
    @property
    def start(self):
        """Start time of data"""
        return self.index[0]
    
    @property    
    def stop(self):
        """Stop time of data"""
        return self.index[-1]
        
    @property
    def species(self):
        """Return name of current species"""
        return self.name
    
    def has_start_stop_acqtamps(self):
        """Checks if start_time and stop_time arrays have valid data"""
        try:
            if not all([isinstance(x, datetime) for x in self.start_acq]):
                raise Exception("Invalid value encountered in start_acq")
            if not all([isinstance(x, datetime) for x in self.stop_acq]):
                raise Exception("Invalid value encountered in stop_acq")
            if not all([len(self) == len(x) for x in [self.start_acq, self.stop_acq]]):
                raise Exception("Lengths of arrays do not match...")
            return True
        except Exception:
            return False
       
    def merge_other(self, other, itp_method="linear", dropna=True):
        """Merge with other time series sampled on different grid
        
        Note
        ----
        
        This object will not be changed, instead, two new Series objects will
        be created and returned
        
        Parameters
        ----------
        other : Series
            Other time series 
        itp_method : str
            String specifying interpolation method (e.g. linear, quadratic)
        dropna : bool
            Drop indices containing NA after merging and interpolation 
            
        Returns
        -------
        tuple
            2-element tuple containing
            
            - this Series (merged)
            - other Series (merged)
        
        """
        if not isinstance(other, Series):
            raise ValueError("Need pandas Series instance (or objects "
                            "inheriting from it)")
        df = DataFrame(dict(s1=self,s2=other)).interpolate(itp_method)
        if dropna:
            df = df.dropna()
        return df.s1, df.s2
        
    def get_data_above_detlim(self):
        """Get fit results exceeding the detection limit 
        
        The detection limit is determined as follows::
        
            self.fit_errs_corr_fac*self.data_err
            
        """
        return self[self > self.fit_errs * self.fit_errs_corr_fac]
        
    def plot(self, date_fmt=None, **kwargs):
        """Plot time series
        
        Uses plotting utility of :class:`Series` object (pandas)        
        
        :param **kwargs: - keyword arguments for pandas plot method
        """
        if not "style" in kwargs:
            kwargs["style"]="--x"
        
        try:
            self.index = self.index.to_pydatetime()
        except:
            pass
        ax = super(DoasResults, self).plot(**kwargs)
        try:
            if date_fmt is not None:
                ax.xaxis.set_major_formatter(DateFormatter(date_fmt))
        except:
            pass
        ax.set_ylabel(self.species)
        return ax
    
    def shift(self, timedelta=timedelta(0.)):
        """Shift time stamps of object
        
        :param timedelta timedelta: temporal shift 
        :returns: shifted :class:`DoasResults` object 
        """
        new = DoasResults(self.values, 
                          self.index + timedelta, 
                          self.start_acq, 
                          self.stop_acq, 
                          self.fit_errs, self.name, self.fit_id, 
                          self.fit_errs_corr_fac)
        if self.has_start_stop_acqtamps:
            new.start_acq += timedelta
            new.stop_acq += timedelta
        return new
    
    def _add__(self, inp):
        s = super(DoasResults, self).__add__(inp)
        return DoasResults(s.values, s.index)   
        
    def __sub__(self, inp):
        s = super(DoasResults, self).__sub__(inp)
        return DoasResults(s.values, s.index)
    
    def __div__(self, inp):
        s = super(DoasResults, self).__div__(inp)
        return DoasResults(s.values, s.index)
    
    def __mul__(self, inp):
        s = super(DoasResults, self).__mul__(inp)
        return DoasResults(s.values, s.index)    
        
    
