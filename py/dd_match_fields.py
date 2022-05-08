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

#20190214 dd_match.py: match dat file with data dictionary (csv2)
import os
import sys
'''
  grep -n DE.HLTH_PROD_LABEL ./dd/*.csv2
    data_dictionary_pharmanet-january-1-1996-onwards.xlsx_dsp_rpt.A

  dd_fields.exe data_dictionary_pharmanet-january-1-1996-onwards.xlsx_dsp_rpt.A
'''
labels_for_file = {}
files = os.popen("ls -1 ~/dd/*.csv2").read().strip().split('\n')
for i in range(0, len(files)):
    files[i] = files[i].strip()
    f = open(os.popen('cygpath -d ' + files[i]).read().strip())
    lines = f.read().strip().split("\n")
    w = lines[0].strip().split(',')
    if w[0].lower() == 'start':
        # print w
        labels = []
        for line in lines:
            line = line.strip()
            w = line.split(',')
            labels.append(w[3].lower())
        labels_for_file[files[i]] = labels # store the labels from this file, according to filename

# field names for extract (no data here):
lines = ["Ft_schlstud.A.dat STUDYID SPECIAL_NEED_CODE_THIS_COLL",
         "DAD STUDYID DIAGX1 DSC ADDATE",
         "MSP STUDYID SPEC ICD9 ICD9_1 ICD9_2 ICD9_3 ICD9_4 ICD9_5 SERVCODE servdate",
         "DES_REP.A DE.STUDYID DE.HLTH_PROD_LABEL DE.DSPD_QTY DE.SRV_DATE",
         "HLTH_REP.A HP.DIN_PIN HP.GEN_DRUG"]
o_f = open("extract_me.csv", "wb")
o_f.write('\n'.join(lines))
o_f.close()
# now attempt to match the labelsets from the file, with the above:
lines = open("extract_me.csv").read().strip().split('\n')
dd_matches = []
for i in range(0, len(lines)):
    line = lines[i].strip().lower().split()
    line = line[1:]
    print ",".join(line)

    max_score, max_f = 0, []
    matched = []
    for f in labels_for_file:
        labels = labels_for_file[f]

        score = 0
        for label_to_match in line:
            # if print "\t", label_to_match
            if label_to_match in labels:
                score += 1
                if label_to_match not in matched:
                    matched.append(label_to_match)

        # make sure to handle multiple matches for the same thing
        if score == max_score:
            max_f.append(f)
        if score > max_score:
            max_f = [f]
            max_score = score

    print "\n\t", max_score, "/", len(line), line, "\n\t-------> ", "MATCH" if max_score==len(line) -1  else ""
    print "\tvarmatch", matched
    for f in max_f:
        print "\t\t", f
        dd_matches.append(f.strip()) # list all dd we want to use to extract

f = open("dd_match_fields_selected_dd.txt", "wb")
f.write('\n'.join(dd_matches))
f.close()
