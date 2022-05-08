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

/* 20190226 unique.cpp:
 * filter for unique last col.:
 * assert that the header for that col says "studyid" */
#include"misc.h"
using namespace std;

int main(int argc, char ** argv){
  if(argc < 2) err("usage: unique.cpp [input file]");

  string dfn(argv[1]);
  string ofn(dfn + string("_unique-studyid.csv"));

  cout << "data input file: " << dfn << endl;
  cout << "data output file: " << ofn << endl;

  ifstream dfile(dfn);
  if(!dfile.is_open()) err(string("failed to open input data file:") + dfn);

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);

  string d;
  string line;
  vector<string> row;
  long unsigned int ci = 0;
  unsigned int col_index = 0;
  map<string, string> unique;

  getline(dfile, line);
  trim(line);
  lower(line);
  row = split(line, ',');
  // in an ideal implementation, logic for first row appears outside of for loop
  for(int k=0; k<row.size(); k++){

    col_index = k; //row.size() - 1;
    d = row[col_index];
    trim(d);
    if(d == "studyid" || d =="study-id" || d=="pc.studyid" || d == "de.studyid") break;
  }
  outfile << line << endl;
  if(d != "studyid" && d != "study-id" && d != "pc.studyid" && d != "de.studyid" ) err("last col field name studyid expected");

  // in the future we should reimplement getline to read whole file into ram if can, or use ramless, different interleaves or latencies
  while(getline(dfile, line)){
    row = split(line, ',');
    d = row[col_index];
    trim(d);
    if(unique.count(d) < 1) unique[d] = line;
    ci ++;
  }
  dfile.close();

  cout << "outputting last unique lines..." << endl;
  for(map<string, string>::iterator it = unique.begin(); it != unique.end(); it++){
    outfile << it->second << endl;
  }
  outfile.close();

  return 0;
}
