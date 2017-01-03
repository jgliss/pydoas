Remarks for DOAS analysis
#################################

.. note:: 
    This code does not yet represent any features to perform DOAS fits itself but
    only vor reading and visualising DOAS fit results retrieved using some DOAS
    analysis software (e.g. DOASIS) which writes fit results in text based resultfiles. 
    
In order for the whole thing to work, please read the following information 
carefully as it will be related to below.

Generally, when dealing with DOAS data, one can distinguish between 2 setups:

    1. Pure time series data (more imporant for e.g. SO2 camera evaluations). This means no (or little) variation in the instrument positioning. In the exemplary case of SO2 cameras for instance, the viewing direction is of camera - and thus also the usually embedded DOAS - are pointing into a volcanic plume for a long time without changing the viewing direction. This data can be subset into single time windows each of which may represent a certain amount of spectra recorded in this time window. The time windows may indicate individual events (i.e. changed reference spectrum used for DOAS fit; moved camera to clear sky...). Normally this yields fit result files (usually .txt or .dat or something like that)  corresponding to these time windows. Here, a new result file means: something changed, e.g.
       
           i. The used reference spectrum
           #. The scan number (number of added spectra)
           #. The viewing direction of the DOAS
    
    #. DOAS scanning results\nHere, individual fit result files often represent one scan and parameters such as elevation or azimuth angle of the instrument change in between individual spectra of the scan. In this case, a new result file usually means: a new scan.\n However strictly spoken, from the "read-in" perspective it is the same than in 1., namely one result file corresponding to a certain time window (the time window covered by the DOAS scan).

In any case, one thing is the same for both scenarios: while the individual 
result files for each time window (*W*) may indicate "some" change of "something" 
there is one more dimension to the whole thing, namely the number (*N*) of different
fits (or fit scenarios) applied to each time window considered. So in fact it 
is to be expected that *NxM* result files exist. For this software to work, 
each fitscenario should have an ID (e.g. f01so2) which should occur in the file
name of the corresponding fitscenario in order for the code to be able to 
extract the important information from this scenario (e.g. SO2 SCDs for all
spectra fitted in *W*). These ids have to be specified in the code below and 
also which information is to be extracted from this file. 

How this information is extracted depends on the resultfiles itself, there are
two options:

    1. The resultfile (e.g. tab delimited) has a header with info strings (e.g.
       "BrO-SCD" for the column number indicating the BrO fit results). In this 
       case, the columns do not have to specified explicitely but it is enough to
       provide a UNIQUE substring which is used to find the column and extract the
       data.
    #. The result file has no header, then each column number to be extracted 
       for each resultfile has to be provided.