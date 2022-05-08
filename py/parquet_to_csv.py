#  Copyright 2019 Province of British Columbia
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
'''convert Apache parquet format file to csv 20190620

Could break if the data are very large.. didn't try!'''
import os
import sys
import pandas as pd
import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.parquet as pq

def err(msg):
    print("Error: " + str(msg))
    sys.exit(1)

if len(sys.argv) < 2:
    err("Usage: parquet_to_csv [input file name.parquet]")

fn = sys.argv[1]
if not os.path.exists(fn):
    err("could not file file: " + fn)

if not fn.split(".")[-1] == "parquet":
    err(".parquet file expected")

open(fn + '.csv', 'wb').write(pq.read_table(fn).to_pandas().to_csv().encode())
