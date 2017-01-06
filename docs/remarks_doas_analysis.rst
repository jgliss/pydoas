Remarks for the DOAS analysis
#############################

This code does not include any features to perform the DOAS analysis itself but only for reading and visualising DOAS fit results retrieved using a suitable DOAS analysis software (e.g. DOASIS) with fit results being stored in text files (.txt, .csv, .dat, etc.).
    
The result files are expected to be formatted in a tabular style where columns define individual parameters (e.g. fitted gas column densities of individual species, start acquistion, number of co-added spectra) and the rows correspond to individual spectra. Each result file hence corresponds to a certain *time interval* (containing *N* spectra) and to one *specific DOAS fit scenario* (i.e. fit interval, fitted species, DOAS fit settings, etc). 
The file names of the result files are therefore required to include a **unique ID which can be used on data import in order to identify the fit scenario** (e.g. f01so2, f02bro). Furthermore, the result files are required to include a header row which is used to identify the individual import columns and which can be specified in the file *import_info.txt* which is part of the package data. 