# -*- coding: utf-8 -*-
"""pydoas example script 2

In this script, a new import type is defined aiming to import the fake
data files in the package data folder "./data/fake_resultfiles
In this example, the import is performed based on specifications of the 
data columns rather than based on searching the header lines of the 
resultfiles.

After import, the an exemplary scatter plot of fake species 3 is performed
for the two fit IDs specified.

"""
import pydoas
from os.path import join, exists
from collections import OrderedDict as od

### Path for output storage
out_path = join(".", "scripts_out")

def load_fake_results():
    ### Get data path
    files, path = pydoas.inout.get_data_files(which = "fake")
    
    ### Specify default import parameters 
    # (this does not include resultfile columns of DOAS fit results)
    meta_import_info =  od([("type", "fake"),
                            ("access_type", "col_index"),
                            ("has_header_line" , 1),
                            ("time_str_formats", ["%Y%m%d%H%M"]),
                            ("file_type", "csv"),
                            ("delim", ";"),
                            ("start", 0), #col num
                            ("stop", 1), #col num
                            ("bla" , "Blub"), #invalid (for test purpose)
                            ("num_scans", 4)]) #colnum
    
    # You could create a new default data type now by calling
    # pydoas.inout.write_import_info_to_default_file(meta_import_info)
    # which would add these specs to the import_info.txt file and which
    # would allow for fast access using 
    # meta_info_dict = pydoas.inout.get_import_info("fake")
    
    import_dict = {'species1'   : [2, ['fit1']], #column 2, fit result file 1
                   'species2'   : [2, ['fit2']], #column 2, fit result file 2
                   'species3'   : [3, ['fit1', 'fit2']]} #column 3, fit result file 1 and 2
    
    stp = pydoas.dataimport.ResultImportSetup(path, result_import_dict =\
                import_dict, meta_import_info = meta_import_info)
    
    #: Create Dataset object for setup...
    return pydoas.analysis.DatasetDoasResults(stp)

if __name__ == "__main__":
    from matplotlib.pyplot import show
    ds = load_fake_results()
    ax = ds.scatter_plot("species3", "fit1", "species3", "fit2",\
                    species_id_zaxis = "species1", fit_id_zaxis = "fit1")
    ax.set_title("Ex.2, scatter + regr, fake species3")
    show()
    print "Outpath %s, exists (y/n) %s" %(out_path, exists(out_path))
    ax.figure.savefig(join(out_path, "ex2_out1_scatter.png"))