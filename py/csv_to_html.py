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
''' 20190911 convert csv to html table with colouring based on quartile
'''
from misc import *

if len(args) < 2:
    err("csv_to_html [input csv file name]")

lines = open(args[1]).readlines()
#hdr = lines[0]
#lines = lines[1:]

ofn = args[1] + ".html"
o_f = wopen(ofn)

o_f.write("<html>\n")
o_f.write("<table>\n")

for i in range(0, len(lines)):
    w = lines[i].strip().split(',')
    w = [wi.strip() for wi in w]

    o_f.write("\t<tr>\n")

    for j in range(0, len(w)):
        try:
            w[j] = w[j].replace("n05a", "antipsychotic")
            w[j] = w[j].replace("n05b", "anxiolytic")
            w[j] = w[j].replace("n06a", "antidepressant")
            w[j] = w[j].replace("n07b", "addictive_disorder_drug")
            w[j] = w[j].replace("n06b", "stimulants")
        except:
            pass
        bg_style = ""
        cc = ""
        bc = "ffffff"
        d = w[j]
        if i > 0:
            try:
                d = float(w[j])
                if d < .25:
                    bc = "00ff00"
                    cc = "ff00ff"
                elif d < .5:
                    bc = "008000"
                    cc = "ff7fff"
                elif d < .75:
                    bc = "800000"
                    cc = "7fffff"
                elif d < 1.:
                    bc = "ff0000"
                    cc = "00ffff"
                bg_style = 'style="background-color:#' + bc + ';color:' + cc + ';"'
                d = round(d, 5)
            except:
                pass

        o_f.write("\t\t<td " + bg_style + ">")
        o_f.write(str(d))
        o_f.write("</td>\n")
    o_f.write("\t</tr>\n")


o_f.write("</table>\n")
o_f.write("</html>")

o_f.close()
