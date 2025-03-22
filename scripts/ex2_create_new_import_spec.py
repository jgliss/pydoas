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
from os.path import join
from collections import OrderedDict as od

from SETTINGS import SAVE_DIR, SAVEFIGS, ARGPARSER, DPI, FORMAT

def main():
    ### create some fake results:
    
    ### Get data path
    _, path = pydoas.inout.get_data_files(which="fake")
    
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
    ds = pydoas.analysis.DatasetDoasResults(stp)
    
    ax = ds.scatter_plot("species3", "fit1", "species3", "fit2",\
                    species_id_zaxis = "species1", fit_id_zaxis = "fit1")
    ax.set_title("Ex.2, scatter + regr, fake species3")
    
    if SAVEFIGS:
        ax.figure.savefig(join(SAVE_DIR, "ex2_out1_scatter.%s" %FORMAT),
                          format=FORMAT, dpi=DPI)

    ### IMPORTANT STUFF FINISHED (Below follow tests and display options)
    
    # Import script options
    options = ARGPARSER.parse_args()
    
    # If applicable, do some tests. This is done only if TESTMODE is active: 
    # testmode can be activated globally (see SETTINGS.py) or can also be 
    # activated from the command line when executing the script using the 
    # option --test 1
    if int(options.test):
        import numpy.testing as npt
        from os.path import basename
        
        npt.assert_array_equal([],
                               [])
        
        # check some propoerties of the basemap (displayed in figure)

        npt.assert_allclose(actual=[],
                            desired=[],
                            rtol=1e-7)
        print("No tests implemented in script: %s" %basename(__file__)) 
    try:
        if int(options.show) == 1:
            from matplotlib.pyplot import show
            show()
    except:
        print("Use option --show 1 if you want the plots to be displayed")
    
if __name__ == "__main__":
    main()