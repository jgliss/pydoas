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
from numpy import asarray, full, polyfit, poly1d, logical_and, polyval
from pandas import Series, DataFrame
from matplotlib.pyplot import subplots
from matplotlib.dates import DateFormatter

#from .setup import ResultImportSetup
from .helpers import to_datetime
from .dataimport import DataImport, ResultImportSetup
            
class DatasetDoasResults(object):
    """A Dataset for DOAS fit results import and processing"""
    def __init__(self, setup=None, init=1, **kwargs):
        """Initialisation of object
        
        :param ResultImportSetup setup: setup specifying  all necessary import 
            settings (please see documentation of :class:`ResultImportSetup`
            for setup details)
        :param **kwargs: alternative way to setup ``self.setup`` 
            (:class:`ResultImportSetup` object), which is only used in case
            no input parameter **setup** is invalid. Valid keyword arguments
            are input parameters of :class:`ResultImportSetup` object.
            
        """
        self.setup = None
        self.raw_results = {}
        
        self.load_input(setup, **kwargs)
        if init:
            self.load_raw_results()
        #self.change_time_ival(start,stop)
            
    def load_input(self, setup=None, **kwargs):
        """Process input information
        
        Writes ``self.setup`` based on setup
        
        :param setup: is set if valid (i.e. if input is 
            :class:`ResultImportSetup`)        
        :param **kwargs: - keyword arguments for new :class:`ResultImportSetup`
            (are used in case first parameter is invalid)
        """
        if not isinstance(setup, ResultImportSetup):
            setup = ResultImportSetup(**kwargs)
        self.setup = setup
    
    @property
    def base_path(self):
        """Returns current basepath of resultfiles (from ``self.setup``)"""
        return self.setup.base_path
        
    @property
    def start(self):
        """Returns start date and time of dataset (from ``self.setup``)"""
        return self.setup.start
        
    @property
    def stop(self):
        """Returns stop date and time of dataset (from ``self.setup``)"""
        return self.setup.stop
    
    @property
    def dev_id(self):
        """Returns device ID of dataset (from ``self.setup``)"""
        return self.setup.dev_id
    
    @property
    def import_info(self):
        """Returns information about result import details"""
        return self.setup.import_info
        
    def change_time_ival(self, start, stop):
        """Change the time interval for the considered dataset
        
        :param datetime start: new start time
        :param datatime stop: new stop time
        
        .. note::
        
            Previously loaded results will be deleted
            
        """
        if isinstance(start, datetime):
            self.start = start
        if isinstance(stop, datetime):
            self.stop = stop
        self.raw_results = {}
        
    def load_raw_results(self):
        """Try to load all results as specified in ``self.setup``"""
        if not self.setup.complete():
            raise AttributeError("Import setup is not complete")
        access = DataImport(self.setup)
        if access.data_loaded:
            self.raw_results = access.results
            self.set_start_stop_time()
            return True
        return False
    
    def has_data(self, fit_id, species_id, start=None, stop=None):
        """Checks if specific data is available"""
        if not (fit_id in self.raw_results and species_id in\
                                                self.raw_results[fit_id]):
            return False
        if all([isinstance(x, datetime) for x in [start, stop]]):
            ts = self.raw_results[fit_id]["start"]
            if not any([start < x < stop for x in ts]):
                return False
        return True
    
    def get_spec_times(self, fit):
        """Returns start time and stop time arrays for spectra to a given fit"""

        start = asarray(self.raw_results[fit]["start"])
        stop = asarray(self.raw_results[fit]["stop"])
        return start, stop
           
            
    def set_start_stop_time(self):
        """Get start/stop range of dataset"""
        start_acq, stop_acq = [], []
        
        for fit_id in self.raw_results:
            print(fit_id)
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
            print(("Could not return meta info, unknown meta ID %s" %meta_id))
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
            print(("Failed to load DOAS results, invalid fit ID %s" %fit_id))
            return False
        m, start, stop = self.get_start_stop_mask(fit_id, start, stop)
        if not sum(m):
            print ("Failed to load DOAS results, no data found for "
                            "specified time interval..")
            return False
        dat = self._get_data(species_id, fit_id)[m]
        times = start + (stop - start) / 2
        dat_err = self._get_data((species_id + "_err"), fit_id)[m]
        return DoasResults(dat, times, start, stop, dat_err, species_id,\
                                                                fit_id, 3)

    """
    HELPERS
    """
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
            
    """
    PLOTTING ETC...
    """
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
        :param bool linF
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
    """
    FITTING / OPTIMISATION ETC...
    """
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

        print(("Item %s could not be found..." %key))
    
    def __setitem__(self, key, val):
        """Change attribute value using bracket syntax"""
        for k,v in list(self.__dict__.items()):
            if k == key:
                self.__dict__[key] = val
                return               
        print(("Item %s could not be updated..." %key))
    
    def __str__(self):
        """String representation"""
        return ("\nDOAS result dataset\n-------------------\n" + str(self.setup))

class DoasResults(Series):
    """Data time series object inheriting from :class:`pandas.Series` for
    handling and analysing DOAS fit results
    
    :param arraylike data: DOAS fit results (column densities)
    :param arraylike index: Time stamps of data points
    :param arraylike fit_errs: DOAS fit errors
    :param string species_id: String specifying the fitted species
    :param string fit_id: Unique string specifying the fit scenario used
    :param int fit_errs_corr_fac: DOAS fit error correction factor
    
    .. todo::
    
        Finish magic methods, i.e. apply error propagation, think about time
        merging etc...
        
    """
    fit_errs = None
    start_acq = []
    stop_acq = []
    fit_id = None
    fit_errs_corr_fac = None
    def __init__(self, data, index = None, start_acq = [], stop_acq = [],\
                            fit_errs = None, species_id = "", fit_id = "",\
                                fit_errs_corr_fac = 1.0):
        if isinstance(data, Series):
            index = data.index
            species_id = data.name
            data = data.values
        super(DoasResults, self).__init__(data, index, name = species_id)
        
        self.fit_errs = fit_errs

        self.fit_id = fit_id        
        self.fit_errs_corr_fac = fit_errs_corr_fac
        self.start_acq = start_acq
        self.stop_acq = stop_acq
         
    @property
    def start(self):
        """Start time of data"""
        try:
            return self.index[0]
        except:
            pass
    
    @property    
    def stop(self):
        """Stop time of data"""
        try:
            return self.index[-1]
        except:
            pass
        
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
            if not all([len(self) == len(x) for x in [self.start_acq,\
                                                            self.stop_acq]]):
                raise Exception("Lengths of arrays do not match...")
            return True
        except Exception as e:
            print((repr(e)))
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
        
#==============================================================================
#     def __div__(self, data):
#         if not isinstance(data, SpectralResults):
#             raise TypeError("Invalid divisor")
#         id=self.speciesID+data.speciesID
#         fitid=self.fit_id+data.fit_id
#         return SpectralResults(self.data/data.data,fit_errs=None, speciesID=id,\
#             fit_id=fitid, start=self.specTimes.start,stop=self.specTimes.start)
#==============================================================================
    
#==============================================================================
#     def shift(self):
#         """Shift series index"""
#         shifted = super(DoasResults, self).shift(*args, **kwargs)
#         return 
#==============================================================================
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
        #ax.xaxis.set_major_formatter(date_formatter)
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
        
        
        
    """Magic methods"""
    def _add__(self, inp):
        s = super(DoasResults, self).__add__(inp)
        return DoasResults(s.values, s.index)#, self.start_acq, self.stop_acq)    
        
    def __sub__(self, inp):
        s = super(DoasResults, self).__sub__(inp)
        return DoasResults(s.values, s.index)#, start_acq = None, stop_acq)
    
    def __div__(self, inp):
        s = super(DoasResults, self).__div__(inp)
        return DoasResults(s.values, s.index)#, self.start_acq, self.stop_acq)
    
    def __mul__(self, inp):
        s = super(DoasResults, self).__mul__(inp)
        return DoasResults(s.values, s.index)#, self.start_acq, self.stop_acq)    
        
    
