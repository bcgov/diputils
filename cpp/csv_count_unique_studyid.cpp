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

/* 20190726 count unique studyid from a csv */
#include"misc.h"
using namespace std;

int main(int argc, char ** argv){
  if(argc < 2) err("usage: csv_count_unique_studyid [input file]");
  str dfn(argv[1]);
  str ofn(dfn + string("_count_unique_studyid"));
  cout << "data input file: " << dfn << endl;
  cout << "data output file: " << ofn << endl;

  ifstream dfile(dfn);
  if(!dfile.is_open()) err(str("failed to open input data file:") + dfn);
  ofstream outfile(ofn);
  if(!outfile.is_open()) err(str("failed to write-open file:") + ofn);

  str d, line;
  vector<str> row;
  long unsigned int ci = 0;
  unsigned int n_fields = 0;
  unsigned int col_index = 0;
  set<str> unique; // count unique studyid

  // find which col. the studyid field is in
  getline(dfile, line);
  trim(line);
  lower(line);
  row = split(line, ',');
  n_fields = row.size();
  // in an ideal implementation, logic for first row appears outside of for loop
  int k;
  for0(k, n_fields){
    col_index = k;
    d = row[col_index];
    trim(d);
    if(d == "studyid" || d =="study-id" || d=="pc.studyid" || d == "de.studyid") break;
  }
  if(d != "studyid" && d != "study-id" && d != "pc.studyid" && d != "de.studyid" ) err("col field name studyid expected");

  // in the future we should reimplement getline to read whole file into ram if can, or use ramless, different interleaves or latencies
  while(getline(dfile, line)){
    row = split(line, ',');
    d = row[col_index];
    trim(d);
    unique.insert(d);
    ci ++;
  }
  dfile.close();

  // output the number of unique studyid, to file
  outfile << unique.size() << endl;
  outfile.close();
  return 0;
}
