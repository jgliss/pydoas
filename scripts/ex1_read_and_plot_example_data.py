# -*- coding: utf-8 -*-
"""pydoas example script 1

Introductory script illustrating how to import data from DOASIS 
resultfiles. The DOASIS result file format is specified as default in the
package data file "import_info.txt". 
Creates a result data set using DOASIS example data and plots some examples

"""
import pydoas
import matplotlib.pyplot as plt
from os.path import join

### Options
save_figs = True

### Path for output storage
out_path = join(".", "scripts_out")

def import_example_results():
        
    ### Get example data base path and all files in there
    files, path = pydoas.get_data_files("doasis")
    
    ### Device ID of the spectrometer (of secondary importance)
    dev_id = "avantes"
    
    ### Data import type (DOASIS result file format)
    res_type = "doasis"
    
    ### Specify the the import details
    
    # here, 3 x SO2 from the first 3 fit scenario result files (f01, f02, f03) 
    # BrO from f04, 2 x O3 (f02, f04) and OClO (f04)
    import_dict = {'so2'  : ['SO2_Hermans_298_air_conv',\
                                                     ['f01','f02','f03']],
                   'bro'  : ['BrO_Wil298_Air_conv',['f04']],
                   'o3'   : ['o3_221K_air_burrows_1999_conv',\
                                                         ['f02', 'f04']],
                   'oclo' : ['OClO_293K_Bogumil_2003_conv',['f04']]}
    
    ### Specify the default fit scenarios for each species
    
    # After import, the default fit scenarios for each species are used
    # whenever fit scenarios are not explicitely specified
    default_dict = {"so2"  :   "f03",
                    "bro"  :   "f04",
                    "o3"   :   "f04",
                    "oclo" :   "f04"}
    
    #: Create import setup object
    stp = pydoas.dataimport.ResultImportSetup(path, result_import_dict =\
            import_dict, default_dict = default_dict, meta_import_info = res_type,\
            dev_id = dev_id)

    #: Create Dataset object for setup...
    ds = pydoas.analysis.DatasetDoasResults(stp)
    
    #: ... and load results
    ds.load_raw_results()
    
    return ds

def plot_some_examples(ds):
    """Plots some example data from a result dataset"""
    
    plt.close("all")
    fig1, axes = plt.subplots(2, 2, figsize = (16, 8), sharex = True)
    ax = axes[0,0]
    
    #load all SO2 results
    r0 = ds.get_results("so2")
    r1 = ds.get_results("so2", "f01")
    r2 = ds.get_results("so2", "f02")
    
    #plot all SO2 results in top left axes object
    r0.plot(style = "-b", ax = ax, label = "so2 (default, f03)")
    r1.plot(style = "--c", ax = ax, label = "so2 (f01)")
    r2.plot(style = "--r", ax = ax, label = "so2 (f02)").set_ylabel(\
                                                            "SO2 [cm-2]")
    ax.legend(loc = 'best', fancybox = True, framealpha = 0.5,\
                                                      fontsize = 9)
    ax.set_title("SO2")
    fig1.tight_layout(pad = 1, w_pad = 3.5, h_pad = 3.5)
    
    #now load the other species and plot them into the other axes objects
    ds.get_results("bro").plot(ax = axes[0, 1], label = "bro",\
                                title = "BrO").set_ylabel("BrO [cm-2]")
    ds.get_results("o3").plot(ax = axes[1, 0], label = "o3",\
                                title = "O3").set_ylabel("O3 [cm-2]")
    ds.get_results("oclo").plot(ax = axes[1, 1], label = "oclo", title =\
                                        "OClO").set_ylabel("OClO [cm-2]")
    
    # Now calculate Bro/SO2 ratios of the time series and plot them with 
    # SO2 shaded on second y axis    
    bro = ds.get_results("bro")
    so2 = r0#ds.get_results("so2")
    broso2 = bro/so2
    
    fig2, axis = plt.subplots(1,1)
    broso2.plot(ax = axis, style = " o")
    axis.set_ylabel("BrO/SO2")
    so2.plot(ax = axis, kind = "area", secondary_y = True, alpha = 0.3).\
                                                set_ylabel("SO2 CD [cm-2]")
    axis.set_title("Plot of BrO/SO2 ratio for pydoas example data")
    
    plt.show()
    
    if save_figs:
        fig1.savefig(join(out_path, "ex1_out1.png"))
        fig2.savefig(join(out_path, "ex1_out2.png"))

if __name__ == "__main__":
    ds = import_example_results()
    plot_some_examples(ds)
    
    