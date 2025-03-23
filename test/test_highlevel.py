# -*- coding: utf-8 -*-
"""
Pydoas high level test module

Author: Jonas Gliß
Email: jonasgliss@gmail.com
License: GPLv3+
"""
import pytest
import pydoas
import numpy.testing as npt

@pytest.fixture(scope="module")
def example_dataset():
    files, path = pydoas.get_data_files("doasis")
    ### Specify the the import details
    
    # here, 3 x SO2 from the first 3 fit scenario result files (f01, f02, f03) 
    # BrO from f04, 2 x O3 (f02, f04) and OClO (f04)
    import_dict = {'so2'  : ['SO2_Hermans_298_air_conv',
                            ['f01','f02','f03']],
                   'bro'  : ['BrO_Wil298_Air_conv',['f04']],
                   'o3'   : ['o3_221K_air_burrows_1999_conv', ['f02', 'f04']],
                   'oclo' : ['OClO_293K_Bogumil_2003_conv', ['f04']]}
     ### Specify the default fit scenarios for each species
    
    # After import, the default fit scenarios for each species are used
    # whenever fit scenarios are not explicitely specified
    default_dict = {"so2"  :   "f03",
                    "bro"  :   "f04",
                    "o3"   :   "f04",
                    "oclo" :   "f04"}
    
    # Device ID of the spectrometer (of secondary importance)
    dev_id = "avantes"
    
    # Data import type (DOASIS result file format)
    res_type = "doasis"
    #: Create import setup object
    stp = pydoas.\
        dataimport.ResultImportSetup(path, 
                                     result_import_dict=import_dict,
                                     default_dict=default_dict, 
                                     meta_import_info=res_type,
                                     dev_id=dev_id)

    #: Create Dataset object for setup...
    ds = pydoas.analysis.DatasetDoasResults(stp)
    ds.load_raw_results()
    return ds

def test_dataset_lowlevel(example_dataset):
    ds = example_dataset
    raw = ds.raw_results
    
    npt.assert_array_equal([sum([x in raw.keys() 
                                for x in ["f01", "f02", "f03", "f04"]]),
                            ds.get_default_fit_id("so2"),
                            ds.get_default_fit_id("bro"),
                            ds.get_default_fit_id("oclo")],
                            [4, "f03", "f04", "f04"])

    so2_fit_ids = ds.import_info["so2"][1]
    vals=[]
    
    for fid in so2_fit_ids:
        vals.append(raw[fid]["so2"].mean())
        vals.append(raw[fid]["so2_err"].mean())
        
    o3_fit_ids = ds.import_info["o3"][1]
    for fid in o3_fit_ids:
        vals.append(raw[fid]["o3"].mean())
        vals.append(raw[fid]["o3_err"].mean())
        
    vals.extend([raw["f01"]["delta"].mean(),
                 raw["f01"]["chi2"].mean(),
                 raw["f01"]["texp"].sum(),
                 raw["f01"]["lon"].mean(),
                 raw["f01"]["lat"].mean(),
                 raw["f01"]["rms"].mean(),])

    npt.assert_allclose(actual=vals,
                        desired=[1.0835821818181818e+18, 
                                 1.7266218181818182e+16, 
                                 6.610916636363636e+17, 
                                 1.8958227272727274e+17, 
                                 9.626614500000001e+17, 
                                 1.2611768181818182e+16, 
                                 1.377051818181818e+18, 
                                 5.511040909090909e+17, 
                                 1.8492713636363635e+18, 
                                 2.3963863636363636e+16, 
                                 0.005684863636363637, 
                                 0.0002420967818181818, 
                                 5078.07, 
                                 15.016000000000004, 
                                 37.76599999999999, 
                                 0.0010376686363636363],
                        rtol=1e-7)
    
def test_main_results(example_dataset):
    ds = example_dataset
    #load all SO2 results
    so2_default = ds.get_results("so2")
    so2_fit01 = ds.get_results("so2", "f01")
    so2_fit02 = ds.get_results("so2", "f02")
    
    #plot all SO2 results in top left axes object
    
    #now load the other species and plot them into the other axes objects
    bro=ds.get_results("bro")
    o3=ds.get_results("o3")
    oclo=ds.get_results("oclo")
    # Now calculate Bro/SO2 ratios of the time series and plot them with 
    # SO2 shaded on second y axis    
    bro_so2 = bro/so2_default
    oclo_so2 = oclo/so2_default
    o3_so2 = o3/so2_default
    o3_so2_f01 = o3/so2_fit01
        
    vals = [so2_default.mean(),
            so2_default.std(),
            so2_fit01.mean(),
            so2_fit02.mean(),
            o3.mean(),
            o3.std(),
            bro.mean(),
            oclo.mean(), 
            bro_so2.mean(),
            oclo_so2.mean(),
            o3_so2.median(),
            o3_so2_f01.median()]
    
    npt.assert_allclose(actual=vals,
                        desired=[9.626614500000001e+17, 
                                 9.785535879339162e+17, 
                                 1.0835821818181818e+18, 
                                 6.610916636363636e+17, 
                                 1.8492713636363635e+18, 
                                 1.2135385847822042e+18, 
                                 126046170454545.45, 
                                 42836762272727.27, 
                                 0.0001389915245877655, 
                                 7.579933107191676e-05, 
                                 4.046278032004655, 
                                 3.4814157916895985],
                        rtol=1e-7)