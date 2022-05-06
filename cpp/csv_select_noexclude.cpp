// Copyright 2019 Province of British Columbia
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/* 20190303 csv_select:
 * filter a given CSV file for records where a given field matches the same field in the other file (somewhere)

Can use this for filtering a dataset for a specific cohort
(as represented by studyid listed in a separate file)

Example (python) from run_select_cohort.py:
  
  import os
  import sys
  files = open("msp_files.txt").read().strip().split("\n")
  for f in files:
    cmd = "csv_select cohort.csv_studyid studyid " + f
    print cmd
    a = os.system(cmd)
*/
#include"misc.h"
#include<cmath>

int main(int argc, char ** argv){
  int is_studyid = false;
  if(argc < 4) err("usage: csv_select [file to filter by] [field name] [file to filter] .. [last file to filter");

  string select_filename(argv[1]); // name of file to select by
  ifstream f_s;
  f_s.open(select_filename);
  if(!f_s.is_open()) err("failed to open input file");
  //mfile f_s(select_filename, "rb"); // if this was too big to keep in mem, could use rewind() to re-scan it
  string s_f_name(argv[2]);

  if(s_f_name == str("studyid")) is_studyid = true;

  unsigned int n_files = argc - 3;
  vector<string> file_names;

  unsigned int i;
  for0(i, n_files){
    cout << " r " << argv[i + 3] << endl;
    file_names.push_back(string(argv[i + 3]));
    FILE * f = fopen(argv[i + 3], "rb");
    if(!f) err("failed to open file");
    fclose(f);
  }
  cout << "number of files: " << n_files << "filenames: " << file_names << endl;

  string s;
  int s_f_i = -1; // selected field index
  set<string> id; // cohort id's
  vector<str> words;
  long unsigned int l_i = 0; // line nummber

  cout << "select field name: " << s_f_name << endl;
  getline(f_s, s);
  cout << "cohort file header: " << s << endl;
  trim(s);
  lower(s);
  words = split(s);
  for0(i, words.size()) if(words[i] == s_f_name) s_f_i = i;
  if(s_f_i < 0) err("failed to find selected field");

  while(getline(f_s, s)){
    trim(s);
    // cout << " " << s;
    lower(s);
    words = split(s);
    trim(words[s_f_i]);
    if(is_studyid){
      if(words[s_f_i].size() != 10){
        err("input data wrong studyid format");
      }
    }
    id.insert(words[s_f_i]);
  }
  //cout << endl;
  f_s.close(); // free up the memory
  if(id.size() == 1) cout << "\tselection: " << id << endl;

  unsigned int j;
  unsigned long int n_matches = 0;
  for0(j, n_files){
    unsigned int nf = 0; // number of fields, this file
    ifstream f_f;
    cout << "r " << file_names[j] << endl;
    f_f.open(file_names[j]);
    if(!f_f.is_open()) err("failed to open input file");
    string ofn(file_names[j] + "_select-" + select_filename + ".csv"); //cout << " +w " << ofn << endl;

    ofstream outf;
    outf.open(ofn);
    if(!outf.is_open()) err("failed to open output file"); // if(!outf) err("failed to open output file");

    s_f_i = -1;
    bool matches_this_iter = false;

    getline(f_f, s);
    trim(s);
    lower(s);
    cout << "hdr: " << s << endl;
    words = split(s);
    nf = words.size();
    int selected = false;
    l_i = 1;
    size_t f_siz = fsize(file_names[j]);

    /* make sure for this file, we can match the name of the appropriate field */
    for0(i, words.size()){
      trim(words[i]);
      vector<str> bytes(split(words[i], '.'));
      if(words[i] == s_f_name || (bytes.size() > 1 && bytes[1] == s_f_name)){
        s_f_i = i;
        cout << "selected field index: " << s_f_i << " selected field: " << words[s_f_i] << endl;
      }
    }
    if(s_f_i < 0) err("failed to find selected field"); // this should happen before we do the work.
    outf << s << endl; // write header

    str d;

    while(getline(f_f, s)){
      //trim(s);
      //lower(s);
      words = split(s);
      /* qc or data integrity checking. should have specific scripts to do this. */
      if(words.size() != nf){
        words = split_special(s);
        if(words.size() != nf){
          cout << words << endl;
          cout << "Unexpected number of fields (" << words.size() << ") at line number: " << l_i << " expected #: " << nf << endl;
          err("Remediation failed: wrong number of fields");
        }
      }
      d = words[s_f_i];
      trim(d);
      lower(d);

      if(is_studyid && d.length() != 10){
        cout << words << endl;
        cout << "line number: " << l_i << endl;
        err("wrong number of digits");
      }
      if(id.count(d) > 0){
        outf << endl << s;
        matches_this_iter = true;
        n_matches ++;
      }

      if((++l_i) % 100000 ==0){
        size_t p = f_f.tellg();
        cout << "%" << 100. * float(p) / float(f_siz) << " matches " << n_matches << endl; // << ceil(100. * float(n_matches) / float(l_i -1)) << endl;
        matches_this_iter = false;
      }
    }
    f_f.close();
    outf.close();
  }

  cout << "size of filter id set:" << id.size() << endl;
  //cout << "size of filter id set that matched target set: " << id_linked.size() << endl;
  cout << "number of matches: " << n_matches << endl;
  set<const char *>::iterator it;

  return 0;
}
