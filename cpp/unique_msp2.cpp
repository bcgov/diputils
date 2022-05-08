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
/* 20190228 unique_msp.cpp: filter a series of msp data files for unique transactions
studyid, pracnum, servdate, icd9 --> file_year N */
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

  system("mkdir out");

  str ofn(string("out/msp_unique.csv"));
  cout << "data output file: " << ofn << endl;

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);

  outfile << string("studyid,pracnum*,servdate,icd9,file_i,line_n\n");
  outfile.flush();
  str line;
  vector<str> row;
  long unsigned int row_count = 0;
  int ind[4]; for(i = 0; i < 4; i++) ind[i] = -1;

  set<const char *> unique;
  string sep(",");

  time_t t0; time(&t0); time_t t1;

  for(j = 0; j < filenames.size(); j++){
    cout << "data input file: " << filenames[j] << endl;
    ifstream dfile(filenames[j]);

    getline(dfile, line);
    row = split(line, ',');
    for(i = 0; i < row.size(); i++){
      if(row[i] == str("studyid")) ind[0] = i;
      if(row[i] == str("pracnum*"))ind[1] = i;
      if(row[i] == str("servdate"))ind[2] = i;
      if(row[i] == str("icd9")) ind[3] = i;
    }
    for(i = 0; i < 4; i++) if(ind[i] == -1) err("missing a field");

    while(getline(dfile, line)){
      row = split(line, ',');
      string d(row[ind[0]] + sep + row[ind[1]] + sep + row[ind[2]] + sep + row[ind[3]]);
      if(unique.count(d) == 0){
        unique[d] = row_count;
        // cout << d << sep << row_count << endl;
      }
      row_count ++;
    }
    // while(getline)
    cout << "closing file.." << endl;
    dfile.close();
  }

  cout << "outputting last unique lines..." << endl;
  for(map<str, long unsigned int>::iterator it = unique.begin(); it != unique.end(); it++){
    stringstream ss;
    ss << it->second;
    #pragma push_macro("str")
    #undef str
    outfile << it->first + sep + ss.str() << endl;
    #pragma pop_macro("str")
    outfile.flush();
  }
  outfile.close();
  return 0;
}
