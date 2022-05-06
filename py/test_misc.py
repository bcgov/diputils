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

from misc import *

def test_misc_csv_read():
    """test reading csv data from a file"""
    r = csv_reader("../test/test.csv")
    fields = r.hdr()
    data = str(fields)
    while True:
        row = r.row()
        if not row: break
        data += '\n' + str(row)

    assert(data == """
['EVT_CODE*', 'EVT_DATE.DE', 'CODE', 'AGE', 'FRST', 'LST', 'SPEC', 'de.id']
['tea', '2018/01/01', 'X', '35', 'PRE', 'WHO', 'BUG', '1']
['coffee', '2018/05/05', 'X', '35', 'JAN,Z', 'WHO', 'FRG', '1']
['water', '2018/01/01', 'Y', '35', 'TAN', 'POST', 'CAT', '2']
    """.strip())

def test_misc_csv_read_inmemory():
    """test reading csv data from memory"""
    r = csv_reader(["fieldname_a,fieldname_b",
                    "mo,bo",
                    "go,zo",
                    "fo,po"])
    fields = r.hdr()
    data = str(fields)
    while True:
        row = r.row()
        if not row: break
        data += '\n' + str(row)
    assert(data=="""
['fieldname_a', 'fieldname_b']
['mo', 'bo']
['go', 'zo']
['fo', 'po']
    """.strip())

test_misc_csv_read()
test_misc_csv_read_inmemory()
