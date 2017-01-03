# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from os.path import join, exists
from os import listdir
import csv
from numpy import asarray, shape #full, polyfit, poly1d, logical_and, polyval, shape

from .inout import get_import_info
#from .setup import ResultImportSetup

class ResultImportSetup(object):
    """Setup class for spectral result imports from text like files """
    def __init__(self, base_path = None, start = None, stop = None,\
                result_import_dict = {}, default_dict = {},\
                doas_fit_err_factors = {}, res_type = "doasis", dev_id = "",\
                lt_to_utc_offset = timedelta(0.0)):
        """
        :param dict result_import_dict: specify file and header information for 
            import. Keys define the used abbreveations after import, the values 
            to each key consist of a list with 2 elements: the first specifies 
            the UNIQUE string which is used to identify this species in the
            header of a given Fit result file, the second entry is a list with 
            arbitrary length containing the fit scenario IDs defining from 
            which fit scenario result files this specific species is to be 
            extracted.
        
            Example::
            
                result_import_dict = {"so2" : ['SO2_Hermans', ['f01','f02']],
                                      "o3"  : ['o3_burrows'], ['f01']]}
            
            Here ``so2`` and "o3" are imported, the data column
            in the result files is found by the header string 
            ``'SO2_Hermans'`` / ``'o3_burrows'`` and this species is imported 
            from all fit scenario result files with fit Ids ``["f01", "f02"]`` 
            (UNIQUE substrings in FitScenario file names.
            
            This is how a filename could look like:
            
                *D130909_S0628_i6_f19_r20_f01so2.dat*
                
            This exemplary filename convention is used by the author of this 
            library when performing an automated DOAS analysis using DOASIS 
            software package `DOASIS 
            <https://doasis.iup.uni-heidelberg.de/bugtracker/projects/doasis/>`_.
            
            The delimiter for retrieving info from these file names is "_", the first
            substring provides info about the date (day), the second about the start 
            time of this time series (HH:MM), 3rd, 4th and 5th information about first 
            and last fitted spectrum number and the corresponding number of the 
            reference spectrum used for this time series and the last index about the
            fit scenario (fitID).
            
            To make a long story short: 
            
                *for this input routine you only need a hint about the used fit 
                scenario in the filename*
        
        :param dict default_dict: specify default species, e.g.::
        
            dict_like = {"so2"     :   "f02",
                         "o3"      :   "f01"}
                        
        :param dict doas_fit_err_factors: fit correction factors (i.e. factors by which
            the DOAS fit error is increased)
            
            dict_like = {"so2"     :   "f02",
                         "o3"      :   "f01"}
                        
        
        """
        self.id = "ResultImportSetup"
        self.base_path = base_path
        self.start = start
        self.stop = stop
        self.lt_to_utc_offset = lt_to_utc_offset
        
        self.dev_id = dev_id
        self.res_type = res_type
        
        self.import_info = result_import_dict
        self.default_fit_ids = {}
        self.doas_fit_err_factors = {}
        
        self.check_time_stamps()
        
        self.set_defaults(default_dict)
        self.set_fitcorr_factors(doas_fit_err_factors)
    
    def set_basepath(self, path):
        """Set the current basepath of the result files"""
        try:
            if exists(path):
                self.base_path = path
                return True
        except Exception as e:
            print repr(e)
            return False
    
    def set_start_time(self, dt):
        """Set the current start time
        
        :param datetime dt: start time of dataset
        
        """
        if not isinstance(dt, datetime):
            print ("Start time %s could not be updated" %dt)
            return False
        self.start = dt
        self.check_time_stamps()
        return True
    
    def set_stop_time(self, dt):
        """Set the current start time
        
        :param datetime dt: start time of dataset
        
        """
        if not isinstance(dt, datetime):
            print ("Stop time %s could not be updated" %dt)
            return False
        self.stop = dt
        self.check_time_stamps()
        return True
        
    def check_time_stamps(self):
        """Check if time stamps are valid and if not, set"""
        if not isinstance(self.start, datetime):
            self.start = datetime(1900, 1, 1) #start time of represented data
        if not isinstance(self.stop, datetime):
            self.stop = datetime(3000, 1, 1) #stop time of represented data  
    
    def complete(self):
        """Checks if basic information is available"""
        miss = []
        if not isinstance(self.base_path, str) or not exists(self.base_path):
            miss.append("base_path")
        if not all([isinstance(x, datetime) for x in [self.start, self.stop]]):
            miss.extend(["start", "stop"])
        if not bool(self.import_info):
            miss.append("import_info")
        if len(miss) > 0:
            return False
        return True
        
    def set_defaults(self, dict_like):
        """Update default fit IDs for fitted species, scheme::
        
            dict_like = {"so2"     :   "f02",
                         "o3"      :   "f01"}
                      
        """
        fit_ids = self.get_fit_ids()
        if not bool(fit_ids):
            #print "Could not set default, fit IDs not accessible..."
            return False
        for species, info in self.import_info.iteritems():
            if dict_like.has_key(species):
                v = dict_like[species]
                print ("Found default fit info for %s in input dict: %s"
                                                            %(species, v))
            else:
                v = info[1][0]
                print ("Failed to find default fit info for %s in input dict, "
                    "use first fit in import info dict: %s " %(species, v))
            self.default_fit_ids[species] = v
        return True
    
    def set_fitcorr_factors(self, dict_like):
        """Set correction factors for uncertainty estimate from DOAS fit errors
        
        :param dict dict_like: dictionary specifying correction factors for 
            DOAS fit errors (which are usually underestimated, see e.g.
            `Gliss et al. 2015 <http://www.atmos-chem-phys.net/15/5659/
            2015/acp-15-5659-2015.html>`_) for individual fit scenarios, e.g.::
            
                dict_like = {"f01"   :   4.0,
                             "f02"   :   2.0}
        
        Default value is 3.0.
        
        """
        facs = {}        
        for fit_id in self.fit_ids:
            if dict_like.has_key(fit_id):
                facs[fit_id] = dict_like[fit_id]
            else:
                facs[fit_id] = 3.0
        self.doas_fit_err_factors = facs
     
    @property
    def xs(self):
        """Returns list with xs names"""
        return self.get_xs_names
        
    def get_xs_names(self):
        """Set and return the string IDs of all fitted species"""
        xs = []
        for key, val in self.import_info.iteritems():
            if val[0] in xs:
                print ("Error: %s was already found with a different key. "
                            "Current key: %s. Please check fit import settings" 
                                                            %(val[0], key))
            else:
                xs.append(val[0])
        xs.sort()
        return xs

    def get_fit_ids_species(self, species_id):
        """Find all fit scenarios which contain results of species
        
        :param str species_id: string ID of fitted species (e.g. SO2)
        
        """
        if not species_id in self.import_info.keys():
            print ("Error: species with ID " + str(species_id) + " not "
                "available in ResultImportSetup")
            return 0
        return self.import_info[species_id][1]
    
    @property
    def fit_ids(self):
        """Returns list with all fit ids"""
        return self.get_fit_ids()
        
    def get_fit_ids(self):
        """Get all fit id abbreveations
        
        Gets all fit ids (i.e. keys of fit import dict ``self.import_info``)        
        """
        ids = []
        for key, val in self.import_info.iteritems():
            sublist = val[1]
            for substr in sublist:
                if substr not in ids:
                    ids.append(substr)
        ids.sort()
        return ids
    
    def __getitem__(self, key):
        """Get a class attribute using bracketed syntax"""
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        print "Class attribute %s does not exist in ResultImportSetup" %key
    
    def __setitem__(self, key, val):
        """Set a class attribute using bracketed syntax"""
        if self.__dict__.has_key(key):
            self.__dict__[key] = val
        print "Class attribute %s does not exist in ResultImportSetup" %key
    
    def __str__(self):
        """String representation of this class"""
        s=("\nSetup\n---------\n\n"
            "ID: %s\n"
            "Base path: %s\n" 
            "Start: %s\n"
            "Stop: %s\n"
            %(self.id, self.base_path, self.start, self.stop))
        s = s + "n\Absorption cross sections\n"
        for key, val in self.import_info.iteritems():
            s = s + "%s: %s\n" %(key, val[0])
        s = s + "Fit scenario IDs\n%s\n" %self.fit_ids
            
        return s
           
class DataImport(object):
    """A class providing reading routines of DOAS result files 
    
    Here, it is assumed, that the results are stored in FitResultFiles, tab 
    delimited whereas the columns correspond to the different variables 
    (i.e. fit results, metainfo, ...) and the rows to the individual spectra.
    General remarks:
    
        1. In general, it is assumed, that the data was evaluated using the
        implemented DOASIS function *fit.AppendResultToFile* in DOASIS (fit 
        corresponds to a "DoasFit class" object)
        
            i. A header (0-th row in file) containing information about 
            parameters
            #. All the other rows correspond to individual spectra
            #. The columns correspond to individual parameters
             
    """
    def __new__(cls, setup):
        if not isinstance(setup, ResultImportSetup):
            raise TypeError("DataImport instance could not be created")
        return super(DataImport, cls).__new__(cls,setup)
    
    def __init__(self, setup):
        self.setup = setup
        
        self.file_type = None
        self.delim = "\t"
        
        self.species_pre_string = ""
        self.fit_err_add_col = 1
        
        self._import_conv_funcs = {"fit_err_add_col" : int}
        
        self._time_str_index = 0
        self.time_str_formats = []
        #:specifying string ids and setup
        self._meta_ids = {el:None for el in self._type_dict.keys()}
        
        self.file_paths = {}
        self.results = {}
        
        self.data_loaded = self.get_data()
    
    @property
    def _type_dict(self):
        """Return dictionary specifying data types of import parameters"""
        return {"start"                 :   datetime.strptime,
                "stop"                  :   datetime.strptime,
                "texp"                  :   float,
                "num_scans"             :   float,
                "azim"                  :   float,
                "elev"                  :   float,
                "lat"                   :   float,
                "lon"                   :   float,
                "geom"                  :   str,
                "chi2"                  :   float,
                "delta"                 :   float,
                "rms"                   :   float,
                "fit_low"               :   float,
                "fit_high"              :   float}
    
    def get_data(self):
        """Load all data"""
        try:
            self.load_result_type_info()
            self.get_all_files()
            self.load_results()
            return True
        except Exception as e:
            print ("Data import failed: %s" %repr(e))
            return False

        
    def load_result_type_info(self):
        """Load import information for result type specified in ``self.setup``
        
        The detailed import information is stored in the package data file
        import_info.txt, this file can also be used to create new filetypes
        """
        info = get_import_info(self.setup.res_type)
        for k,v in info.iteritems():
            self[k] = v
    
    def _update_attribute(self, key, val):
        """Update one of the attributes
        
        Checks if key is class attribute or - alternatively - a valid meta key
        (i.e. key of ``self._meta_ids``) and if so, checks if a specific
        data type for this attribute is required (in ``self._type_dict``). If
        the latter is the case, the input value will only be set if it can be
        converted given the specific type conversion. 
        
        :param str key: valid key of class or ``self._meta_ids`` dict
        :param val: new value
        
        """
        if self._import_conv_funcs.has_key(key):
            try:
                val = self._import_conv_funcs[key](val)
            except:
                print ("Failed to convert input %s, %s into data type %s"
                                    %(key, val, self._import_conv_funcs[key]))
                return False
        if self.__dict__.has_key(key):
            self.__dict__[key] = val
            return True
        if self._meta_ids.has_key(key):
            self._meta_ids[key] = val
            return True
        print "Could not update attribute %s : %s" %(key, val)
        return False
        
    @property
    def base_path(self):
        """Returns current basepath of resultfiles"""
        return self.setup.base_path
        
    @property
    def start(self):
        """Returns start date and time of dataset"""
        return self.setup.start
        
    @property
    def stop(self):
        """ Returns stop date and time of dataset"""
        return self.setup.stop
    
    @property
    def time_str_format(self):
        """Returns datetime formatting info for string to datetime conversion
        
        This information should be available in the resultfile type 
        specification file (package data: data/import_info.txt)        
        """
        return self.time_str_formats[self._time_str_index]
                   
    def init_result_dict(self):
        """Initiate the result dictionary"""
        res = {}
        for fit_id in self.setup.fit_ids:
            res[fit_id] = {} 
            for meta_id in self._meta_ids:
                res[fit_id][meta_id]=[]
            for species, info in self.setup.import_info.iteritems():
                if fit_id in info[1]:
                    res[fit_id][species] = []
                    res[fit_id][species + "_err"] = []
        self.results = res
    
    def get_indices(self, fileheader, dict):
        """Find positions of species in header of result file
        
        :param list fileheader: header row of resultfile
        :param dict dict: dictionary containing species IDs (keys) and the
            corresponding (sub) strings (vals) to find them in the header
    
        """
        ind = {}
        for key,val in dict.iteritems():
            v = self.find_col_index(val, fileheader)
            if v != -1:
                ind[key] = v
        return ind
    
    def find_all_indices(self, fileheader, fit_id):
        """Find all relevant indices for a fit scenario"""
        #load all metainfo indices
        warnings = []
        ind = self.get_indices(fileheader, self._meta_ids)
        #now find indices of all species supposed to be extracted from this fit 
        #scenario
        for species, info in self.setup.import_info.iteritems():
            if fit_id in info[1]:
                substr = self.species_pre_string + info[0]
                idx = self.find_col_index(substr, fileheader)
                if idx != -1:                      
                    ind[species] = idx
                    ind[species + "_err"] = ind[species] + self.fit_err_add_col
                else:
                    warnings.append("Failed to find column index for species %s"
                        " using header search string %s" %(species, substr))
        return ind, warnings
        
    def load_results(self):
        """Load all results 
        
        The results are loaded as specified in ``self.import_setup`` for all 
        valid files which were detected in :func:`get_all_files` which 
        writes ``self.file_paths``
        """
        self.init_result_dict()
        all_warnings = []
        for fit_id in self.setup.fit_ids:
            for file in self.file_paths[fit_id]:
                data = self.read_text_file(file)
                last_index = shape(data)[0]
                #load all metainfo indices
                ind, warnings = self.find_all_indices(data[0], fit_id)
                if bool(warnings):
                    all_warnings.append(warnings)
                datetime.strptime(data[1][ind["start"]], self.time_str_format)

                #Here, the actual import begins
                for k in range(1, last_index):
                    start = datetime.strptime(data[k][ind["start"]],\
                                                        self.time_str_format)
                    if self.start <= start <= self.stop:
                        for key, index in ind.iteritems():
                            try:
                                #try to convert the entry into float
                                self.results[fit_id][key].append(float(\
                                                            data[k][index]))
                            except ValueError:
                                try:
                                    self.results[fit_id][key].append(\
                                        datetime.strptime(data[k][index],\
                                                        self.time_str_format))
                                except:
                                    self.results[fit_id][key].append(\
                                                            data[k][index])
                                
        for key, dic in self.results.iteritems():
            for k, lst in dic.iteritems():
                self.results[key][k] = asarray(lst)
        
        if bool(all_warnings):
            for warning_list in all_warnings:
                for warning in warning_list:
                    print warning
        
    def find_col_index(self, substr, header):
        """Find the index of the column in data
        
        :param str substr: substr identifying the column in header
        :param list header: the header of the data in which index of substr is searched
        
        """
        try:
            return next((i for i, s in enumerate(header) if substr in s), -1)
        except Exception as e:
            print repr(e)
            return -1
    
    def _update_time_str_format(self, data):
        """Set the format strings for datetime info in the result-files"""
        func = self._type_dict["start"]
        col = self.find_col_index(self._meta_ids["start"], data[0])
        if col is -1:
            return 0
        fmts = self.time_str_formats
        for k in range(len(fmts)):
            try:
                func(data[1][col],fmts[k])
                print "Found time string format %s" %fmts[k]
                self._time_str_index = k
                return 1
            except:
                pass
        return 0
        
    def check_time_match(self, data):
        """Check if data is within time interval set by self.start and self.stop
        
        :param list data: data as read by :func:`read_text_file`
        :returns: - bool, Match or no match
        """
        func = self._type_dict["start"]
        col = self.find_col_index(self._meta_ids["start"], data[0])
        if col is -1:
            return 0
        if self.start is None or self.stop is None:
            return 1
        last_index = shape(data)[0]
        #loop over all fitted spectra in the file and find matches
        for k in range(1, last_index):
            t = func(data[k][col], self.time_str_format)
            if self.start < t < self.stop:
                print "Found data file match %s" %t
                return 1
        return 0
    
    @property
    def first_file(self):
        """Get filepath of first file match in ``self.base_path``
        
        This can for instance be read with :func:`read_text_file`
        """
        all = [join(self.base_path, f) for f in listdir(self.base_path) if\
                                                    f.endswith(self.file_type)]
        return all[0]
    
    def init_filepaths(self):
        """Initate the file paths"""
        for fit_id in self.setup.fit_ids:
            self.file_paths[fit_id] = []
            
    def get_all_files(self):
        """Get all valid files based on current settings
        
        Checks ``self.base_path`` for files matching the specified file type, 
        and which include one of the required fit IDs in their name. Files
        matching these 2 criteria are opened and the spectrum times are read 
        and checked. If they match the time interval specified by
        ``self.start`` and ``self.stop`` the files are added to the dictionary 
        ``self.file_paths`` where the keys specify the individual fit scenario 
        IDs.
        
        .. note::
        
            This function does not load data but only assigns the individual
            result files to the fit IDs, the data will then be loaded calling
            :func:`load_results`
                
        """
        self.init_filepaths()
        all_files = [join(self.base_path, f) for f in listdir(self.base_path)\
                                                if f.endswith(self.file_type)]
        #first check if time conversion works
        self._update_time_str_format(self.read_text_file(all_files[0]))
        for fname in all_files:            
            for fit_id in self.setup.fit_ids:
                if fname.find(fit_id) >- 1:
                    data = self.read_text_file(fname)
                    found = self.check_time_match(data)
                    if found:
                        self.file_paths[fit_id].append(fname)
        del data, all_files
     
    def read_text_file(self, p):
        """Read text file using csv.reader and return data as list
        
        :param str p: file path
        :returns list: data 
        """
        with open(p) as f:
            reader = csv.reader(f, delimiter = self.delim)
            data = list(reader)
        return data
    
    def __setitem__(self,key, val):
        """Set item method"""
        self._update_attribute(key, val)


