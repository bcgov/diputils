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

/* 20190228 unique_msp.cpp:
 * filter a series of msp data files for unique transactions
 * studyid, pracnum, servdate, icd9 --> file_year N
 * note: the program is robust to the ordering of the req'd fields */
#include"misc.h"
using namespace std;

int main(int argc, char ** argv){
  int i, j;
  if(argc < 2) err("usage: unique.cpp [input file] .. [input file n]");

  vector<string> filenames;
  for(i = 1; i < argc; i++) filenames.push_back(string(argv[i]));

  for(i = 0; i < filenames.size(); i++){
    /* check all the files actually open before we go ahead.. getting partway through the job would suck*/
    ifstream dfile(filenames[i]);
    if(!dfile.is_open()) err(string("failed to open input data file:") + filenames[i]);
    dfile.close();
  }

  str ofn(string("msp_unique.csv"));
  cout << "data output file: " << ofn << endl;

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);

  outfile.flush();
  str line;
  vector<str> row;
  int ind[4]; for(i = 0; i < 4; i++) ind[i] = -1;

  set<string> unique;
  //map<string, string> unique; //long unsigned int> unique;
  string sep(",");

  time_t t0; time(&t0); time_t t1;

  long unsigned int l_i = 0; // row index of output

  string d;
  for(j = 0; j < filenames.size(); j++){
    cout << "data input file: " << filenames[j] << endl;
    //mfile t(filenames[j], "rb");
    ifstream dfile(filenames[j]);

    getline(dfile, line);
    //t.getline(line); //dfile, line);
    if(l_i == 0) outfile << line << endl;
    row = split(line, ',');
    for(i = 0; i < row.size(); i++){
      if(row[i] == str("studyid")) ind[0] = i;
      if(row[i] == str("pracnum*"))ind[1] = i;
      if(row[i] == str("servdate"))ind[2] = i;
      if(row[i] == str("icd9")) ind[3] = i;
    }
    for(i = 0; i < 4; i++) if(ind[i] == -1) err("missing a field");

    l_i ++; // header row is still a row
    while(getline(dfile, line)){
      row = split(line, ',');
      string icd9(row[ind[3]]);
      trim(icd9);
      if(icd9 != string("")){
        d = (row[ind[0]] + sep + row[ind[1]] + sep + row[ind[2]] + sep + row[ind[3]]);
        if(unique.count(d) < 1){
          unique.insert(d); // alternative (for map<str, unsigned long int> unique): unique[d] = row_index
          outfile << line << endl;
        }
      }
      if((++ l_i) % 100000 ==0){
        // good time to invoke buffer-switch for multithread
        cout << l_i << " " << d << endl;
      }
    }
    dfile.close();
  }
  cout << "writing.." << endl;
  outfile.close();
  return 0;
}
