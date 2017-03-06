This file keeps track of major changes applied to the code after the first 
release of pydoas (version 1.0.1)

06/03/2017
==========

  1. Expanded handling of start / stop time specifications in Setup classes and Dataset classes (for initialisation of working environment) -> now, the user can also provide time stamps (datetime.time objects) or dates (datetime.date objects) as input and they will converted automatically to datetime. 
  2. Included new module helpers.py (helper methods)
  3. Included date formatting option in time series plots of DoasResults class
  4. Included merging functionality for DoasResults class: method ``merge_other``
  