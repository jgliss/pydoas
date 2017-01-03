# -*- coding: utf-8 -*-
from datetime import datetime
from numpy import ndarray, asarray, full, polyfit, poly1d, logical_and, polyval
from bunch import Bunch
from pandas import Series
from pandas.tseries.index import DatetimeIndex
from traceback import format_exc
from matplotlib.pyplot import subplots

from .Setup import DoasResultSetup
from .DataAccess import DataAccess
            
class DataSetSpectralResults(object):
    """A Dataset for DOAS fit results import and processing"""
    def __init__(self, setup = None, **kwargs):
        """Initialisation of object
        
        :param DoasResultSetup setup: setup specifying  all necessary import 
            settings (please see documentation of :class:`DoasResultSetup`
            for setup details)
        :param **kwargs: alternative way to setup ``self.setup`` 
            (:class:`DoasResultSetup` object), which is only used in case
            no input parameter **setup** is invalid. Valid keyword arguments
            are input parameters of :class:`DoasResultSetup` object.
            
        """
        self.setup = None
        self.rawResults = None
        
        self.load_input(setup, **kwargs)
        #self.change_time_ival(start,stop)
            
    def load_input(self, setup = None, **kwargs):
        """Load input (see docs of :func:`self.__init__` for input details)"""
        if not isinstance(setup, DoasResultSetup):
            setup = DoasResultSetup(**kwargs)
        self.setup = setup
    
    @property
    def basePath(self):
        """Returns current basepath of resultfiles (from ``self.setup``)"""
        return self.setup.basePath
        
    @property
    def start(self):
        """Returns start date and time of dataset (from ``self.setup``)"""
        return self.setup.start
        
    @property
    def stop(self):
        """Returns stop date and time of dataset (from ``self.setup``)"""
        return self.setup.stop
    
    @property
    def deviceId(self):
        """Returns device ID of dataset (from ``self.setup``)"""
        return self.setup.deviceId
    
    @property
    def importInfo(self):
        """Returns information about result import details"""
        return self.setup.importInfo
        
    def change_time_ival(self, start, stop):
        """Change the time interval for the considered dataset
        
        .. note::
        
            Previously loaded results will be deleted
            
        """
        if isinstance(start, datetime):
            self.start=start
        if isinstance(stop, datetime):
            self.stop=stop
        self.rawResults=None
        
    def load_raw_results(self):
        if self.setup.ready_2_go():
            access = DataAccess(self.setup)
            self.rawResults = access.results
            self.set_start_stop_time()
    
    def results_available(self,speciesId,fitId):    
        if not bool(self.importInfo):
            return 0
        for key, val in self.importInfo.iteritems():
            if key == speciesId:
                if fitId in val[1]:
                    return 1
        return 0
    
    def get_default_fit_id(self, species):
        """Get the default fit ID (if available) for species
        
        :param str species: str ID of species
        """
        try:
            return self.importInfo.defaultFitIds[species]
        except:
            print "Failed to retrieve default fit ID for species " + str(species)
    
    def get_spec_times(self):
        """Returns start time and stop time arrays
        """
        try:
            start=asarray(self.rawResults["metaInfo"]["start"])
            stop=asarray(self.rawResults["metaInfo"]["stop"])
            return start,stop
        except:
            raise IOError(format_exc())            
            
    def set_start_stop_time(self):
        """Get start/stop range of dataset"""
        start,_ = self.get_spec_times()
        self.setup.start = start.min()
        self.setup.stop = start.max()
        return self.start, self.stop
    
    def get_start_stop_mask(self, start=None, stop=None):
        """Creates boolean mask for data access only in a certain time interval
        """
        if start is None:
            start = self.start
        if stop is None:
            stop = self.stop
        i,f= self.get_spec_times()
        mask=logical_and(i >= start, i <= stop)
        return mask, i[mask], f[mask]
        
    def get_meta_info(self, metaKey, boolMask=None):
        """Get meta info array
        
        :param str metaKey: string ID of meta information
        :param array boolMask: boolean mask for data retrieval
        
        .. note::
        
            Bool mask must have same length as the meta data array
            
        """
        if not self.rawResults["metaInfo"].has_key(metaKey):
            print ("Could not return meta info, unknown meta string ID: " + str(metaKey))
            return 0
        dat = self.rawResults["metaInfo"][metaKey]
        if boolMask is None:
            return dat
        return dat[boolMask]
        
        
    def get_data(self, dataKey, fitId):
        """Access raw data array"""
        try:
            return self.rawResults[fitId][dataKey]
        except:
            print format_exc()
            return False
    
    def get_results(self,species, fitId=None, start=None, stop=None):
        """Get spectral results object
        
        :param str species: string ID of species
        :param str fitID (None): string ID of fit scenario (if None, try to 
            load default fitId)
            
        """
        #(data, species, fitId, start=None,stop=None,dataErr=None,fitResultsRaw=None,fitCorrFac=3)
        try:
            if fitId is None:
                fitId = self.setup.defaultFitIds[species]
            m, start, stop = self.get_start_stop_mask(start,stop)
            dat = self.get_data(species, fitId)[m]
            datErr = self.get_data((species + "Err"), fitId)[m]
            res = SpectralResults(dat, datErr, species, fitId, start, stop, 3)
            return res
        except:
            print format_exc()
            return False
    """
    HELPERS
    """
    def set_default_fitscenarios(self, dictLike):
        try:
            self.importInfo.set_defaults(dictLike)
            return 1
        except:
            return 0
    """
    PLOTTING ETC...
    """
    def plot(self,species, fitId=None, start=None, stop=None, **kwargs):
        """Plot spectral results"""
        res=self.get_results(species, fitId, start, stop)
        if res is not False:
            return res.plot(**kwargs)
        return 0
            
    def scatter_plot(self, speciesX, fitIdX, speciesY, fitIdY, linFitOpt=1, speciesZ=None,\
                            fitIdZ=None, start=None, stop=None, ax=None, **kwargs):
        """Make a scatter plot of two species
        """
        data={}
        resX=self.get_results(speciesX, fitIdX, start, stop)
        resY=self.get_results(speciesY, fitIdY, start, stop)
        data["x"]=resX
        data["y"]=resY
        resZ=None
        if speciesZ is not None and fitIdZ is not None:
            resZ=self.get_results(speciesZ, fitIdZ, start, stop)
        data["z"]=resZ
        if ax is None:
            fig,ax=subplots(1,1)
        else:
            fig=ax.figure.canvas.figure
        if resZ is not None:
            sc=ax.scatter(resX.data,resY.data,15,resZ.data,marker='o',edgecolor='none', **kwargs)
            cb=fig.colorbar(sc,ax=ax, shrink=0.9,**kwargs)    
            cb.set_label(speciesZ + " " + fitIdZ, **kwargs)
        else:
            ax.plot(resX.data,resY.data,**kwargs)
        ax.set_xlabel(speciesX + " " + fitIdX)
        ax.set_ylabel(speciesY + " " + fitIdY)
        ax.grid()
        if linFitOpt:
            self.linear_regression(resX.data,resY.data,0,ax=ax)
        return fig, ax, data
    """
    FITTING / OPTIMISATION ETC...
    """
    def linear_regression(self, xData, yData, mask=None, ax=None):
        """Perform linear regression and return parameters
        """
        if mask is None:
            mask=full(len(yData),True,dtype=bool)
        params=polyfit(xData[mask],yData[mask],1)
        poly=poly1d(params)
        res={"x"    :   params,
             "poly" :   poly}
#==============================================================================
#         func = lambda p, x: p[0] * x + p[1]
#         errFun=lambda p, x, y: (func(p,x) - y)**2
#         
#         yR=yData.max()-yData.min()
#         xR=xData.max()-xData.min()
#         
#         guess=[yR/xR,yData[np.abs(xData).argmin()]]
#         bds = ([-np.inf,-np.inf], [np.inf,np.inf]) #fit param boundaries
#         if throughOriginOpt:
#             bds = ([-np.inf,-yR/1000.], [np.inf,yR/1000.])
#         
#         res = least_squares(errFun, guess, args=(xData, yData), bounds=bds)
#         print ("Linear regression succesful, intial guess:\n" + str(guess) 
#             + "\nAfter regression:\n" + str(res.x))
#==============================================================================
        if ax is not None:
            ax.plot(xData,polyval(poly,xData),"-r", label="Fit result")
        return res
    
    def get_fit_import_setup(self):
        """Get the current fit import setup"""
        return self.setup.importInfo

    def __getitem__(self, key):
        """Get attribute using bracketed syntax"""
        for k,v in self.__dict__.iteritems():
            if k == key:
                return v
            try:
                return v[key]
            except:
                pass

        print "Item %s could not be found..." %key
    
    def __setitem__(self, key, val):
        """Change attribute value using bracket syntax"""
        for k,v in self.__dict__.iteritems():
            if k == key:
                self.__dict__[key] = val
                return               
        print "Item %s could not be updated..." %key
    
    def __str__(self):
        """String representation"""
        return ("\nDOAS result dataset\n-------------------\n" + str(self.setup))
            
class SpectralResults(object):
    """Basic collection of spectral results for further analysis
    
    :param arraylike data: DOAS fit results (column densities)
    :param string species: String specifying the fitted species
    :param string fitId: Unique string specifying the fit scenario used
    :param arraylike start: array with start time stamps of measurements 
    :param arraylike stop: array with stop time stamps of measurements
    :param fitResultsRaw: fitResultsObject which was use to generate the data
    :param int fitCorrFac: DOAS fit correction factor for detection limit
    
    """
    def __init__(self, data, dataErr=None, speciesID="", fitID="",\
                                            start=None,stop=None,fitCorrFac=1):
        self.speciesID=speciesID
        self.fitID=fitID
        self.data=None
        self.dataErr=dataErr
        self.fitCorrFac=fitCorrFac
        self.specTimes=Bunch({"start"   :   start,
                              "stop"    :   stop})
        
        self.set_data(data)
        
    def set_data(self, data):
        """Set data
        
        :param data: input data (accepts pandas.Series and numpy array)
        """
        ts=self.times
        if isinstance(data, Series):
            self.data=data
            if isinstance(data.index, DatetimeIndex):
                self.specTimes.start=data.index.values
            return 1
        elif any(isinstance(data, x) for x in [ndarray, list]):
            self.data=Series(data, ts)
            return 1
        return 0
            
    @property
    def times(self):
        """Acquisition times of all data points"""
        try:
            info=self.specTimes
            if info.start is None:
                print "No time info available, use indices..."
                return None
            elif info.stop is None:
                return info.start
            else:
                return info.start+(info.stop-info.start)/2
        except: 
            print format_exc()
            return None

    @property
    def start(self):
        """Start time of data"""
        try:
            return self.data.index[0]
        except:
            pass
    
    @property    
    def stop(self):
        """Stop time of data"""
        try:
            return self.data.index[-1]
        except:
            pass
        
    def get_data_above_detlim(self):
        """Get fit results exceeding the detection limit 
        
        The detection limit is determined as follows::
        
            self.fitCorrFac*self.dataErr
            
        """
        try:
            cond=self.fitCorrFac*self.dataErr < self.data
            return self.data[cond]
        except:
            print format_exc()
            return None
    
    def __div__(self, data):
        if not isinstance(data, SpectralResults):
            raise TypeError("Invalid divisor")
        id=self.speciesID+data.speciesID
        fitid=self.fitID+data.fitID
        return SpectralResults(self.data/data.data,dataErr=None, speciesID=id,\
            fitID=fitid, start=self.specTimes.start,stop=self.specTimes.start)
            
    def plot(self,**kwargs):
        """Plot 
        """
        try:
            if not "style" in kwargs:
                kwargs["style"]="--x"
            
            ax=self.data.plot(**kwargs)
            ax.set_ylabel(self.speciesID)
            return ax
        except:
            print format_exc()
            
            

    

