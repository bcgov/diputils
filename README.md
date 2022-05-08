# diputils
Utilities to support the [**Data Innovation Program** (DIP)](https://www2.gov.bc.ca/gov/content/data/about-data-management/data-innovation-program). Generally Windows, Mac and Linux environments supported, some aspects may be specific to Windows, Cygwin, or require POPDATA SRE to run

## Features
This package presently supports several big-data friendly operations for tabular data, due to properties of data in DIP environment
* **Fixed width format** w data dictionary or header file specifying field names and widths
* Using DIP metadata, some of which are avail. from BC Data Catalogue
* **Quite large** potentially up to **tens of GB per file** or more
* Duplicate records that need to be de-duplicated
* Zipped

### Guiding principles:
* **Making results obtainable** by increasing the data volume that can be processed, e.g. by incrementally reading files so the main storage of the system becomes the limiting factor (i.e., moving from 10's of GB to 100's-1000's of GB range)
* **Self-contained** / not using dependencies beyond base language features included in python, C/C++ and R. When working in a secure environment, software requests can take weeks to get approved. Therefore, to some degree, having a reference set of functions that are simple and transparent enough to recreate portions of manually (if need be) supports researchers flexibility
* **Language agnostic** using a quick and dirty approach: borrowing from the Unix tradition by making procedures (written in any langauge) available (from any language) using the system interface

In R: 

```system("command_to_run")```

In C/C++:

```system("command to run")```

In python:

```import os; os.system("command_to_run")```

## Project Status
This project is developed and supported by DPD Partnerships and Capacity (PAC) branch and partners incl. BC Wildfire Service (BCWS) Predictive Services Unit 

## Projects Supported incl.
* Race based data initiative (RBD) 
* Dip projects: 
	- CYMH
	- DIP Development
	- Education Special Needs
	- Children in Care (In-Care Network)
* BC Wildfire Service (BCWS) Fuel Type Layer Project

## Contents by Directory (and examples):
### **cpp**: c++ based scripts
- **unique.cpp**: data de-duplication. This script makes is possible to de-duplicate extremely large tables. When it concludes, it indicates how many unique records were retained in the output
- **dd_slice_apply_cohort.cpp**: using a data dictionary, convert a flat-file to CSV format. This version of the script takes a cohort file as input so that only records pertaining to a cohort of interest are retained (can be very helpful to reduce data volume)
- **unique_msp.cpp**: MSP specific: filters MSP (medical services plan) data for unique records, based on several records that define a unique MSP transaction
- **unzp.cpp**: unzip zip files in the present directory in parallel, to get this done faster
- **csv_slice.cpp**: slice certain columns out of a (potentially arbitrarily large) CSV file
-  **csv_sort_date.cpp**: sort a CSV record in order by date
-  **csv_split_year.cpp**: split a large CSV file into per-year portions
-  **csv_split.cpp**: convert a CSV file into a columnar format (multi single-col "CSV" files)
-  **count_col.cpp**: fast counting of outcomes within columnar dataset (single-col "CSV")
-  **csv_select.cpp**: quick and dirty version of SELECT command in SQL 
-  **pqt.cpp**: prototype data compression by: dictionary encoding and bit packing
-  **upqt.cpp**: undo the above compression
-  **csv_cat.cpp**: concatenate CSV files to create a larger (arbitrarily large) one!
- **pnet_check.cpp**: filter pharmanet (PNET) data according to an industry-standard method
 
### **py**: python based scripts
- **get_metadata.py**: fetch DIP metadata from BC Data Catalogue (BCDC)
- **make_fakedata.py**: synthesize DIP data from the above metadata
- **dd_list.py**: find, convert "all" (all at the time of development) data dictionaries available in the environment, to a common cleaned format
- **dd_match_data_file.py**: for a data file, find an acceptable data dictionary to use to open it 
- **df_list.py**: list available data files (flat files) in the POPDATA environment
- **dd_get.py**: pull the "most current" copy of a given table (named by it's file name)
- **csv_to_fixedwidth.py**: convert CSV data to "fixed width" format
- **parquet_to_csv.py**: convert an Apache-parquet format file to CSV format
- **csv_grep.py**: grep operation for csv files that produces output that is also valid CSV with header
- **indent.py**: indent a code file
- **multicore.py**: run jobs listed in a shell script, in parallel
- **dd_sliceapply_all.py**: convert all flat files in a directory, to CSV (finding the data dictionaries automagically etc.)
- **forever.py**: loop a command repeatedly for example when monitoring jobs that run for hours or days
### **R**: R based scripts
### **c**: C based scripts

## Sample use (outside of DIP):
#### get_metadata.py (fetch DIP metadata from DataBC)
Terminal:

```python3 get_metadata.py```

(Alternately, can open in Python IDLE and select RUN from menu, or press F5 key)

#### make_fakedata.py (generate unrealistic fake data to some extent based on DIP metadata from DataBC)
Terminal:

```python3 make_fakedata.py```

(Alternately, can open python scripts in Python IDLE and select RUN from menu, or press F5 key)

Optional arguments:

```python3 make_fakedata.py [minimum number of rows, per file] [maximum number of rows, per file]```

* minimum number of rows, per file: lower bound for random number of rows of synthetic to generate
* maximum number of rows, per file: upper bound for random number of rows of synthetic to generate

**Notes:** CSV format synthetic data (.csv) are supplied alongside zipped fixed-width format synthetic data (.zip) for comparison. In the actual DIP environment
* data are provided in fixed-width format ONLY (no CSV files)
* the data dictionaries don't typically appear in the same folder as the fixed-width files they're associated with. Software for matching fixed-width files with data dictionaries, is provided in this repository 

## Using inside of DIP environment
### Building "diputils" command-line utilities in SRE:

1. copy the contents of this folder into your private folder (R:/$USER/bin/)
- copy the tar.gz file into your home folder, and extract it there...
- this file, bash.bat, etc. should reside in R:/$USER/bin/.. for example, if they were in R:/$USER/bin/diputils-master/ the files should be moved up a level!

2. navigate there (R:/$USER/bin) in Windows Explorer (the file manager)
	- for example, if my user name is "bob", the place to go is:
		R:/bob/bin

3. double-click on bash.bat (bash) to enter the cygwin bash prompt (the
programs should be built automatically)

To check if the utilities are working: can type (followed by pressing return):

```csv_slice```

If programs built correctly you would seem something like:

Error: usage:
        slice.exe [infile] [Field name] .. [Field name n]

4. How to find out where a particular script is: (at the terminal in the bin/ folder) to find csv_slice:

```find ./ -name "csv_slice*"```

in this instance the output was:

./cpp/csv_slice.cpp

./csv_slice.exe

The .cpp file is c++ code in the appropriate folder; the .exe file is the verb
deployed at the terminal

### Notes:
How to find out your user name in linux / Cygwin prompt:

type (followed by return):

```whoami```

For example, if my user name was bob, the terminal should come back and say:

   bob 

## Example uses (not all DIP specific):
### Opening and unpacking data for a cohort ###
This operation may be quite slow and require some manual intervention. Also the process here is likely to only cover some fraction of available 
data sets as new ones have been added since, and there may be issues due to formatting updates

#### Copy a cohort file (csv with studyid col) to (present) tmp folder: ####

```cp /cygdrive/r/.../cohort.csv .```

#### To confirm the file is there ####
Can type: 

```ls```

And press return.

#### Slice out the studyid field ####
A terminal command so have to press return after:

```csv_slice studyid cohort.csv```

#### Examine first 10 lines of the result file ####

```head -10 cohort.csv_slice.csv```

#### Move the studyid-only file to a simpler filename: ####
For convenience: 

```mv cohort.csv_slice.csv studyid.csv```

Then press return. 

#### Fetch and extract all data for a cohort: ####

```sup_cohort studyid.csv```

### Downloading, fetching and unpacking the latest version of a specific data file ###

#### Find pharmanet data ####

```find /cygdrive/r/DATA/ -name "*pharmanet*"```

/cygdrive/r/DATA/2019-04-24/docs/data_dictionary_pharmanet-january-1-1996-onwards.xlsx
/cygdrive/r/DATA/2019-04-24/pharmanet

#### Make a local copy of pharmanet files (subset for your study population): ####
```pnet_get studyid.csv```


**Note: this script needs to be updated to reflect currently available data** [here](https://github.com/ashlinrichardson/diputils/blob/aba1628283d64accd6a01052b2951433d7fbc08d/py/pnet_get.py#L22)

### Converting a "flat file" to csv: ###

First get a copy of the file:

```df_get hlth_prod_final.dat```

And convert it to CSV:

```dd_sliceapply_all hlth_prod_final.dat```

### In-place removal of whitespace characters from end of a file ###
This program is sanity promoting as some programs could interpret terminating newline character as a record, leading to inaccuracies or errors:

```snip studyid.csv```

### Concatenating pharmanet files ###
the script pnet_get above handles this.



### Checking pharmanet files for bad data (according to filtering algorithm provided by MoH subject matter expert) ###

```pnet_check dsp_rpt.dat_dd_sliceapply.csv```

Bad data, if detected, should appear in a separate file.

### Example of analyzing mh drug usage from pnet: ###

Although this script depends on one proprietary table (.xls) that is not provided here, otherwise the script should:
download, fetch, unpack, clean, concatenate, and analyze pharmanet data for a cohort, without intervention.

```pnet_druglist studyid.csv```

## Getting Help
Please contact Ashlin.Richardson@gov.bc.ca for assistance or to provide feedback

## Contributors

## License

Copyright 2020 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
