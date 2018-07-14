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
from datetime import datetime, timedelta
from os.path import join, exists
from os import listdir
import csv
from warnings import warn
from numpy import asarray, shape 

from .inout import get_import_info
from .helpers import to_datetime

class ResultImportSetup(object):
    """Setup class for spectral result imports from text like files """
    def __init__(self, base_dir=None, start=datetime(1900, 1, 1),
                 stop=datetime(3000, 1, 1), meta_import_info="doasis",
                 result_import_dict={}, default_dict={},
                 doas_fit_err_factors={}, dev_id="",
                 lt_to_utc_offset=timedelta(0.0)):
        """
        :param str base_dir: folder containing resultfiles
        :param datetime start: time stamp of first spectrum
        :param datetime stop: time stamp of last spectrum
        
        :param meta_import_info: Specify the result file format and columns
            for meta information (see als file import_info.txt or example
            script 2). Input can be str or dict. In case a string is 
            provided, it is assumed, that the specs are defined in 
            import_info.txt, i.e. can be imported (as dictionary) 
            from this file (using :func:`get_import_info`, e.g. with arg = 
            ``doasis``). If a dictionary is provided, the information is 
            directly set from the provided dictionary. 
                
        :param dict result_import_dict: specify file and header information for 
            import. Keys define the used abbreveations after import, the 
            values to each key consist of a list with 2 elements: the first 
            specifies the UNIQUE string which is used to identify this 
            species in the header of a given Fit result file, the second 
            entry is a list with arbitrary length containing the fit 
            scenario IDs defining from which fit scenario result files this 
            specific species is to be extracted.
        
            Example::
            
                result_import_dict = {"so2" : ['SO2_Hermans', ['f01','f02']],
                                      "o3"  : ['o3_burrows'], ['f01']]}
            
            Here ``so2`` and "o3" are imported, the data column in the 
            result files is found by the header string ``'SO2_Hermans'`` / 
            ``'o3_burrows'`` and this species is imported from all fit 
            scenario result files with fit Ids ``["f01", "f02"]`` 
            (UNIQUE substrings in FitScenario file names.
            
            Exemplary file name:
            
                ``D130909_S0628_i6_f19_r20_f01so2.dat``
                
            This (exemplary) filename convention is used for the example 
            result files shipped with this package (see folder 
            pydoas/data/doasis_resultfiles) which include fit result files
            from the software `DOASIS <https://doasis.iup.uni-heidelberg.
            de/bugtracker/projects/doasis/>`_.
            
            The delimiter for retrieving info from these file names is "_", 
            the first substring provides info about the date (day), the 
            second about the start time of this time series (HH:MM), 3rd, 
            4th and 5th information about first and last fitted spectrum 
            number and the corresponding number of the reference spectrum 
            used for this time series and the last index about the fit 
            scenario (fitID).
            
            Each resultfile must therefore include a unique ID in the file
            name by which it can be identified.
        
        :param dict default_dict: specify default species,
            e.g.::
        
                dict_like = {"so2"     :   "f02",
                             "o3"      :   "f01"}
                        
        :param dict doas_fit_err_factors: fit correction factors 
            (i.e. factors by which the DOAS fit error is increased)::
                
                dict_like = {"so2"     :   "f02",
                             "o3"      :   "f01"}
                             
        :param str dev_id: string ID for DOAS device (of minor importance)
        :param timedelta lt_to_utc_offset: specify time zone offset (will 
            be added on data import if applicable).
                        
        
        """
        self.base_dir = base_dir
        self._start = None
        self._stop = None
        
        self.start = start
        self.stop = stop
        
        self.lt_to_utc_offset = lt_to_utc_offset #currently unused ...
        
        self.dev_id = dev_id
        
        self.import_info = result_import_dict
        self.meta_import_info = {}
        self.default_fit_ids = {}
        self.doas_fit_err_factors = {}
        
        self.check_time_stamps()
        
        self.minimum_meta_keys = ["start", "delim", "access_type",\
                        "has_header_line", "file_type", "time_str_formats"]
        self.set_defaults(default_dict)
        self.set_fitcorr_factors(doas_fit_err_factors)
        
        if isinstance(meta_import_info, str):
            self.meta_import_info.update(get_import_info(meta_import_info))
        elif isinstance(meta_import_info, dict):
            self.meta_import_info.update(meta_import_info)
        
        if not all([x in list(self.meta_import_info.keys()) for x in\
                                            self.minimum_meta_keys]):
            raise ImportError("Please specify at least the following "
                "parameters: %s, available keys are: %s" 
                %(self.minimum_meta_keys, list(self.meta_import_info.keys())))
        if self.access_type == "header_str" and not\
                    self.meta_import_info["has_header_line"]:
            raise Exception("Invalid combination of result file settings: "
                "has_header_line == False and access_type == header_str")
        if not result_import_dict:
            self.auto_detect_
            
    @property
    def start(self):
        """Start time-stamp of data"""
        return self._start
        
    @start.setter
    def start(self, val):
        try:
            self._start = to_datetime(val)
        except:
            warn("Input %s could not be assigned to start time in setup" %val)
    
    @property
    def stop(self):
        """Stop time-stamp of data"""
        return self._stop
        
    @stop.setter
    def stop(self, val):
        try:
            self._stop = to_datetime(val)
        except:
            warn("Input %s could not be assigned to stop time in setup" %val)
    
    @property
    def base_path(self):
        """Old name of base_dir for versions <= 1.0.1"""
        return self.base_dir
        
    def set_start_time(self, dt):
        """Set the current start time
        
        :param datetime dt: start time of dataset
        
        """
        if not isinstance(dt, datetime):
            print(("Start time %s could not be updated" %dt))
            return False
        self.start = dt
        self.check_time_stamps()
        return True
    
    def set_stop_time(self, dt):
        """Set the current start time
        
        :param datetime dt: start time of dataset
        
        """
        if not isinstance(dt, datetime):
            print(("Stop time %s could not be updated" %dt))
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
        exceptions = []
        try:
            if not exists(self.base_dir):
                raise AttributeError("Base directory does not exist")
        except Exception as e:
            exceptions.append(repr(e))
        try:
            if not all([isinstance(x, datetime) for x in [self.start, self.stop]]):
                raise AttributeError("Invalid start / stop timestamps")
        except Exception as e:
            exceptions.append(repr(e))
        try:
            if not bool(self.import_info):
                raise AttributeError("No species import information specified")
        except Exception as e:
            exceptions.append(repr(e))
        if len(exceptions) > 0:
            for exc in exceptions:
                warn(exc)
            return False
        return True
        
    def set_defaults(self, dict_like):
        """Update default fit IDs for fitted species
        
        Scheme::
        
            dict_like = {"so2"     :   "f02",
                         "o3"      :   "f01"}
                      
        """
        fit_ids = self.get_fit_ids()
        if not bool(fit_ids):
            #print "Could not set default, fit IDs not accessible..."
            return False
        for species, info in list(self.import_info.items()):
            if species in dict_like:
                v = dict_like[species]
                print(("Found default fit info for %s in input dict: %s"
                                                            %(species, v)))
            else:
                v = info[1][0]
                print(("Failed to find default fit info for %s in input dict, "
                    "use first fit in import info dict: %s " %(species, v)))
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
            if fit_id in dict_like:
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
        for key, val in list(self.import_info.items()):
            if val[0] in xs:
                print(("Error: %s was already found with a different key. "
                       "Current key: %s. Please check fit import settings" 
                                                            %(val[0], key)))
            else:
                xs.append(val[0])
        xs.sort()
        return xs

    def get_fit_ids_species(self, species_id):
        """Find all fit scenarios which contain results of species
        
        :param str species_id: string ID of fitted species (e.g. SO2)
        
        """
        if not species_id in list(self.import_info.keys()):
            print(("Error: species with ID " + str(species_id) + " not "
                "available in ResultImportSetup"))
            return 0
        return self.import_info[species_id][1]
    
    @property
    def fit_ids(self):
        """Returns list with all fit ids"""
        return self.get_fit_ids()
    
    @property
    def access_type(self):
        """Return the current setting for data access type"""
        return self.meta_import_info["access_type"]
    
    @property
    def HEADER_ACCESS_OPT(self):
        """Checks if current settings allow column identification from file
        header line"""
        if self.access_type == "header_str" and\
                    self.meta_import_info["has_header_line"]:
            return True
        return False
    
    @property
    def FIRST_DATA_ROW_INDEX(self):
        if self.meta_import_info["has_header_line"]:
            return 1
        return 0
        
    def get_fit_ids(self):
        """Get all fit id abbreveations
        
        Gets all fit ids (i.e. keys of fit import dict ``self.import_info``)        
        """
        ids = []
        for key, val in list(self.import_info.items()):
            sublist = val[1]
            for substr in sublist:
                if substr not in ids:
                    ids.append(substr)
        ids.sort()
        return ids
    
    def __getitem__(self, key):
        """Get a class attribute using bracketed syntax"""
        if key in self.__dict__:
            return self.__dict__[key]
        print(("Class attribute %s does not exist in ResultImportSetup" %key))
    
    def __setitem__(self, key, val):
        """Set a class attribute using bracketed syntax"""
        if key in self.__dict__:
            self.__dict__[key] = val
        print(("Class attribute %s does not exist in ResultImportSetup" %key))
    
    def __str__(self):
        """String representation of this class"""
        s=("\nSetup\n---------\n\n"
            "Base path: %s\n" 
            "Start: %s\n"
            "Stop: %s\n"
            %(self.base_dir, self.start, self.stop))
        s = s + "n\Absorption cross sections\n"
        for key, val in list(self.import_info.items()):
            s = s + "%s: %s\n" %(key, val[0])
        s = s + "Fit scenario IDs\n%s\n" %self.fit_ids
            
        return s
           
class DataImport(object):
    """A class providing reading routines of DOAS result files 
    
    Here, it is assumed, that the results are stored in FitResultFiles, 
    tab delimited whereas the columns correspond to the different variables 
    (i.e. fit results, metainfo, ...) and the rows to the individual 
    spectra.
    """
    def __init__(self, setup = None):
        if not isinstance(setup, ResultImportSetup):
            setup = ResultImportSetup()
        self.setup = setup
        
        self.file_type = None
        self.delim = "\t"
        
        self.species_pre_string = ""
        
        self._import_conv_funcs = {"fit_err_add_col" : int}
        
        self._time_str_index = 0
        self.time_str_formats = []
        #:specifying string ids and setup
        self._meta_ids = {el:None for el in list(self._type_dict.keys())}
        
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
        if not exists(self.base_dir):
            raise IOError("DOAS data import failed: result base directory "
                "%s does not exist" %self.base_dir)
        self.load_result_type_info()
        self.get_all_files()
        self.load_results()
        try:
            self.load_result_type_info()
            self.get_all_files()
            self.load_results()
            return True
        except Exception as e:
            print(("Data import failed: %s" %repr(e)))
            return False

    def load_result_type_info(self):
        """Load import information for result type specified in setup
        
        The detailed import information is stored in the package data file
        import_info.txt, this file can also be used to create new filetypes
        """
        info = self.setup.meta_import_info
        #info = get_import_info(self.setup.res_type)
        for k,v in list(info.items()):
            self[k] = v
    
    def _update_attribute(self, key, val):
        """Update one of the attributes
        
        Checks if key is class attribute or - alternatively - a valid meta 
        key (i.e. key of ``self._meta_ids``). If so, checks if a 
        specific data type for this attribute is required (in 
        ``self._type_dict``). If the latter is the case, the input value 
        will only be set if it can be converted given the specific type 
        conversion. 
        
        :param str key: valid key of class or ``self._meta_ids`` dict
        :param val: new value
        
        """
        if key in self._import_conv_funcs:
            try:
                val = self._import_conv_funcs[key](val)
            except:
                print(("Failed to convert input %s, %s into data type %s"
                       %(key, val, self._import_conv_funcs[key])))
                return False
        if key in self.__dict__:
            self.__dict__[key] = val
            return True
        if key in self._meta_ids:
            self._meta_ids[key] = val
            return True
        #print "Could not update attribute %s : %s" %(key, val)
        return False
        
    @property
    def base_dir(self):
        """Returns current basepath of resultfiles"""
        return self.setup.base_dir
        
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
    
    @property
    def fit_err_add_col(self):
        """Return current value for relative column of fit errors"""
        try:
            return self.setup.meta_import_info["fit_err_add_col"]  
        except:
            return 0
            
    def init_result_dict(self):
        """Initiate the result dictionary"""
        res = {}
        for fit_id in self.setup.fit_ids:
            res[fit_id] = {} 
            for meta_id in self._meta_ids:
                res[fit_id][meta_id]=[]
            for species, info in list(self.setup.import_info.items()):
                if fit_id in info[1]:
                    res[fit_id][species] = []
                    res[fit_id][species + "_err"] = []
        self.results = res
    
    def find_valid_indices_header(self, fileheader, dict):
        """Find positions of species in header of result file
        
        :param list fileheader: header row of resultfile
        :param dict dict: dictionary containing species IDs (keys) and the
            corresponding (sub) strings (vals) to find them in the header
    
        """
        ind = {}
        for key, val in list(dict.items()):
            v = self.find_col_index(val, fileheader)
            if v != -1:
                ind[key] = v
        return ind
    
    def find_all_indices(self, fileheader, fit_id):
        """Find all relevant indices for a given result file (fit scenario)
        
        :param list fileheader: list containing all header strings from 
            result file (not required if data access mode is from columns
            see also :func:`HEADER_ACCESS_OPT` in 
            :class:`ResultImportSetup`)
        :param str fit_id: ID of fit scenario (required in order to find 
            all fitted species supposed to be extracted, specified in 
            ``self.setup.import_info``)
        """
        #load all metainfo indices
        warnings = []
        if self.setup.HEADER_ACCESS_OPT:
            ind = self.find_valid_indices_header(fileheader, self._meta_ids)
        else:
            ind = {}
            for key, val in list(self._meta_ids.items()):
                try:
                    ind[key] = int(val)
                except:
                    pass
        #now find indices of all species supposed to be extracted from this fit 
        #scenario
        for species, info in list(self.setup.import_info.items()):
            if fit_id in info[1]:
                if self.setup.HEADER_ACCESS_OPT:
                    substr = self.species_pre_string + info[0]
                    idx = self.find_col_index(substr, fileheader)
                else:
                    print(("set %s col for fit ID %s at column %s"
                           %(species, fit_id, info[0])))
                    idx = info[0] 
                if idx != -1:                      
                    ind[species] = idx
                    ind[species + "_err"] = ind[species] +\
                                                self.fit_err_add_col
                else:
                    warnings.append("Failed to find column index for "
                        "species %s using header search string %s" 
                        %(species, substr))
        return ind, warnings
        
    def load_results(self):
        """Load all results 
        
        The results are loaded as specified in ``self.import_setup`` for all 
        valid files which were detected in :func:`get_all_files` which 
        writes ``self.file_paths``
        """
        # delete all previous results
        self.init_result_dict()
        all_warnings = []
        # loop over different fit IDs
        for fit_id in self.setup.fit_ids:
            # loop over all files corresponding to one fit ID
            for file in self.file_paths[fit_id]:
                data = self.read_text_file(file)
                last_index = shape(data)[0]
                #load all metainfo indices
                ind, warnings = self.find_all_indices(data[0], fit_id)
                if bool(warnings):
                    all_warnings.append(warnings)
                print(("First spectrum time: %s" %datetime.strptime(data[\
                    self.setup.FIRST_DATA_ROW_INDEX][ind["start"]],\
                                                self.time_str_format)))

                #Here, the import begins (loop over data rows in file)
                for k in range(self.setup.FIRST_DATA_ROW_INDEX, last_index):
                    start = datetime.strptime(data[k][ind["start"]],\
                                              self.time_str_format)
                    if self.start <= start <= self.stop:
                        for key, index in list(ind.items()):
                            try:
                                if key in ["start", "stop"]:
                                    self.results[fit_id][key].append(\
                                        datetime.strptime(data[k][index],\
                                                    self.time_str_format))
                                else:
                                    #try to convert the entry into float
                                    self.results[fit_id][key].append(\
                                                    float(data[k][index]))
                            except:
                                self.results[fit_id][key].append(\
                                                        data[k][index])
                                
                                
        for key, dic in list(self.results.items()):
            for k, lst in list(dic.items()):
                self.results[key][k] = asarray(lst)
        
        if bool(all_warnings):
            for warning_list in all_warnings:
                for warning in warning_list:
                    print(warning)
        
    def find_col_index(self, substr, header):
        """Find the index of the column in data
        
        :param str substr: substr identifying the column in header
        :param list header: the header of the data in which index of substr is searched
        
        """
        try:
            return next((i for i, s in enumerate(header) if substr in s), -1)
        except Exception as e:
            print((repr(e)))
            return -1
    
    def _update_time_str_format(self, data):
        """Set the format strings for datetime info in the result-files"""
        func = self._type_dict["start"]
        if self.setup.HEADER_ACCESS_OPT:
            col = self.find_col_index(self._meta_ids["start"], data[0])
        else:
            col = self.setup.meta_import_info["start"]
        if col is -1:
            return 0
        fmts = self.time_str_formats
        for k in range(len(fmts)):
            try:
                print((data[self.setup.FIRST_DATA_ROW_INDEX][col]))
                print((fmts[k]))
                func(data[self.setup.FIRST_DATA_ROW_INDEX][col],fmts[k])
                print(("Found time string format %s" %fmts[k]))
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
        if self.setup.HEADER_ACCESS_OPT:
            col = self.find_col_index(self._meta_ids["start"], data[0])
        else:
            col = self.setup.meta_import_info["start"]
        if col is -1:
            return 0
        if self.start is None or self.stop is None:
            return 1
        last_index = shape(data)[0]
        #loop over all fitted spectra in the file and find matches
        for k in range(self.setup.FIRST_DATA_ROW_INDEX, last_index):
            t = func(data[k][col], self.time_str_format)
            print(t)
            if self.start < t < self.stop:
                print(("Found data file match %s" %t))
                return 1
        return 0
    
    @property
    def first_file(self):
        """Get filepath of first file match in ``self.base_dir``
        
        This can for instance be read with :func:`read_text_file`
        """
        all = [join(self.base_dir, f) for f in listdir(self.base_dir) if\
                                                    f.endswith(self.file_type)]
        return all[0]
    
    def init_filepaths(self):
        """Initate the file paths"""
        for fit_id in self.setup.fit_ids:
            self.file_paths[fit_id] = []
            
    def get_all_files(self):
        """Get all valid files based on current settings
        
        Checks ``self.base_dir`` for files matching the specified file type, 
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
        if not exists(self.base_dir):
            raise IOError("DOAS data import failed: result base directory "
                "%s does not exist" %self.base_dir)
        self.init_filepaths()
        all_files = [join(self.base_dir, f) for f in listdir(\
                         self.base_dir) if f.endswith(self.file_type)]
        if not len(all_files) > 0:
            raise IOError("Data import failed, no files of type %s could "
                "be found in current base folder: %s" #
                %(self.file_type, self.base_dir))
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
            reader = csv.reader(f, delimiter=str(self.delim))
            data = list(reader)
        return data
    
    def __setitem__(self,key, val):
        """Set item method"""
        self._update_attribute(key, val)


