# diputils
Utilities to support the [**Data Innovation Program** (DIP)](https://www2.gov.bc.ca/gov/content/data/about-data-management/data-innovation-program). Generally Windows, Mac and Linux environments supported, some aspects may be specific to Windows, Cygwin, or require POPDATA SRE to run

## Features
This package presently supports several big-data friendly operations for tabular data, due to properties of data in DIP environment
* **Fixed width format** w data dictionary or header file specifying field names and widths
* Using DIP metadata, some of which are avail. from BC Data Catalogue
* Quite large, potentially **up to tens of GB per file**
* Zipped

### Guiding principles:
* **Making results obtainable** by increasing the data volume that can be processed, e.g. by incrementally reading files so the main storage of the system becomes the limiting factor (i.e., moving from 10's of GB to 100's-1000's of GB range)
* **Self-contained** / not using dependencies beyond base language features included in python, C/C++ and R. When working in a secure environment, software requests can take weeks to get approved. Therefore, to some degree, having a reference set of functions that are simple and transparent enough to recreate portions of manually (if need be) supports researchers flexibility

## Project Status
This project is developed and supported by DPD Partnerships and Capacity (PAC) branch and partners incl. BC Wildfire Service (BCWS) Predictive Services Unit 

## Projects Supported incl.
* Dip projects: CYMH / DIP Development proeject / Children in Care (in care network) / Educ. Special needs project
* Race based data initiative (RBD) 
* BC Wildfire Service (BCWS) Fuel Type Layer Project

## Contents by Directory (and examples):
### **cpp**: c++ based scripts
### **py**: python based scripts
- **get_metadata.py**: fetch DIP metadata from BC Data Catalogue (BCDC)
- **make_fakedata.py**: synthesize DIP data from the above metadata
- **csv_to_fixedwidth.py**: convert CSV data to "fixed width" format
- **indent.py**: indent a code file
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
(Alternately, can open in Python IDLE and select RUN from menu, or press F5 key)

Optional arguments:

```python3 make_fakedata.py [minimum number of rows, per file] [maximum number of rows, per file]```
* minimum number of rows, per file: lower bound for random number of rows of synthetic to generate
* maximum number of rows, per file: upper bound for random number of rows of synthetic to generate

**Notes:** CSV format synthetic data (.csv) are supplied alongside zipped fixed-width format synthetic data (.zip) for comparison. In the actual DIP environment
* data are provided in fixed-width format ONLY (no CSV files)
* the data dictionaries don't typically appear in the same folder as the fixed-width files they're associated with. Software for matching fixed-width files with data dictionaries, will soon be provided in this repository 

## Example Usage (inside of DIP)
### Building "diputils" command-line utilities in SRE:

1. copy the contents of this folder into your private folder (R:/$USER/bin/)
- copy the tar.gz file into your home folder, and extract it there...
    - this file, bash.bat, etc. should reside in R:/$USER/bin/...
       .. for example, if they're in R:/$USER/bin/bin/ the files.. 
 	.. would need to be moved up a level!

2. navigate there (R:/$USER/bin) in Windows Explorer (the file manager)
	- for example, if my user name was "bob", the place to go is:
		R:/bob/bin

3. double-click on bash.bat (bash) to enter the cygwin bash prompt (the
programs should be built automatically)

You can check if the utilities are working by typing (followed by pressing
return):
```
csv_slice
```

If the programs built correctly you would see:

Error: usage:
        slice.exe [infile] [Field name] .. [Field name n]

4. How to find out where a particular script is:
at the terminal in the bin/ folder,

to find csv_slice:
```
find ./ -name "csv_slice*"
```

in this instance the output was:
  ./cpp/csv_slice.cpp
  ./csv_slice.exe

the .cpp file is c++ code in the appropriate folder; the .exe file is the verb
deployed at the terminal
  - These utilities use a language-agnostic format where all scripts are
    represented as verbs available on the command-line

Notes:
How to find out your user name in linux / Cygwin prompt:

type (followed by return):
```
whoami
```
For example, if my user name was bob, the terminal should come back and say:

   bob 

Example uses:

1. Opening and unpacking all the data for a cohort (may be slow and require
some manual intervention.. also is likely to only cover a limited number of 
data sets as new ones have been added since.. and formats have changed, there
may be issues):

a) copy a cohort file (csv with studyid col) to the tmp folder:
```
cp /cygdrive/r/.../cohort.csv .
```

b) to confirm the file is there type: 
```
ls
```
And press return.

c) slice out the studyid field (it's a terminal command so have to press return)

```
csv_slice studyid cohort.csv
```

d) examine the first 10 lines of the result file:
```
head -10 cohort.csv_slice.csv
```

e) move the studyid-only file to a simpler filename:
```
mv cohort.csv_slice.csv studyid.csv
```

f) fetch and extract all data for a cohort:
```
sup_cohort studyid.csv		
```

2. Downloading, fetching and unpacking the latest version of a specific data
file:

a) find pharmanet data
```
find /cygdrive/r/DATA/ -name "*pharmanet*"
```
/cygdrive/r/DATA/2019-04-24/docs/data_dictionary_pharmanet-january-1-1996-onwards.xlsx
/cygdrive/r/DATA/2019-04-24/pharmanet

b) make a local copy of pharmanet files (subset for your study population):
```
pnet_get studyid.csv
```

3. Converting a "flat file" to csv (get a copy of a file first, then convert to csv):
```
df_get hlth_prod_final.dat
dd_sliceapply_all hlth_prod_final.dat
```

4. In-place removal of whitespace characters from the end of a file (some programs
could interpret terminating newline character as a record?)
```
snip studyid.csv
```

5. concatenating pharmanet files
	covered in 2. b)

6. checking pharmanet files for bad data (according to filtering algorithm..)
```
pnet_check dsp_rpt.dat_dd_sliceapply.csv
```
	(bad data, if detected, should appear in a separate file)

7. example of analyzing mh drug usage from pnet:
 (note: this script should now download, fetch, unpack, clean, concatenate,
and analyze pharmanet data for a cohort-- no intervention required)
```
pnet_druglist studyid.csv
```

#### []()

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
