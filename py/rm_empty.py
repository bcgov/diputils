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

# 20190401 remove empty folders, recursively
import os
import sys

def rm_empty(path, rm_root=True):
    if not os.path.isdir(path):
        return
    # rm empty subdirs
    files = os.listdir(path)
    for f in files:
        p = os.path.join(path, f)
        if os.path.isdir(p):
            rm_empty(p)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and rm_root:
        print "rm " + str(path)
        os.rmdir(path)

rm_root = False
rm_empty(os.getcwd(), rm_root)