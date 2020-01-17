# diputils
Utilities to assist Data Innovation Program (DIP)

## Features

This package presently supports:
* producing synthetic data resembling the data residing within the Data Innovation Program's (DIP) Secure Research Environment

Given that access to DIP data are restricted, synthetic data resembling the DIP data are useful for:
* training purposes
* sharing examples of data with partner ministries
* troubleshooting code outside the SAE with the help from knowledge experts
* demonstrations within the Digital Platforms and Data (DPD) Division 

Properties of data 
- Arbitrarily large 
- Zipped
- Fixed width format, with data dictionary / header
- Produced from DIP metadata available on BC Data Catalogue

## Project Status

This project is currently under development and actively supported by the DPD Partnerships and Capacity (PAC) branch

## Contents by Directory:

#### [/](.//)
- get_metadata.py: fetch DIP metadata from BC Data Catalogue (BCDC)
- make_fakedata.py: synthesize DIP data from the above metadata

## Usage:

#### get_metadata.py
'''python3 get_metadata.py'''

#### make_fakedata.py
'''python3 make_fakedata.py'''

## Relevant Repositories

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
