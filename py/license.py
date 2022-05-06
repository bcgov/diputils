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
'''Add license header to files with specified extension and in expected
locations'''
from misc import *
license = '''   Copyright 2019 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.'''

license_lines = license.split("\n")
license_lines = ["  " + line.strip() for line in license_lines]
comment = {}
comment['py'] = '#'
comment['c'] = "//"
comment['R'] = '#'
comment['cpp'] = "//"
comment['h'] = "//"

def iter_ext(ext):
    for e in ext:
        my_license_lines = [(comment[e] + line) for line in license_lines]
        print(my_license_lines[0])

        file_names = os.popen('find ./ -name "*.' + e + '"').readlines()
        for f in file_names:
            f = f.strip()
            file_lines = open(f).readlines()
            file_lines = [line.rstrip() for line in file_lines]

            if(file_lines[0] != my_license_lines[0]):
                print("\tneed header: " + f.strip())
                new_file_lines = [line.rstrip() for line in my_license_lines]
                new_file_lines.append("");
                for line in file_lines:
                    new_file_lines.append(line)
                open(f, "wb").write("\n".join(new_file_lines).encode())

files = iter_ext(['py', 'cpp', 'h', 'c', 'R'])
