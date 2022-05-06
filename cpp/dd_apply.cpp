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

/* 20190212 dd_apply.cpp
 apply data dictionary to translate fixedwidth to csv !!!!!
 
Note that CSV files can/may be smaller than their fixed-width counterparts */
#include"misc.h"
#include<ctime>
#include<string>
#include<fstream>
#include<iostream>
#include<algorithm>
using namespace std;

int main(int argc, char ** argv){
  if(argc < 3) err("usage: dd_apply.cpp [data dictionary.csv] [data input.dat]");
  str ddf(argv[1]);
  str dtf(argv[2]);
  str ofn(dtf + str("_dd_apply.csv"));

  cout << "data dictionary file: " << ddf << endl;
  cout << "data input file: " << dtf << endl;
  cout << "output file: " << ofn << endl;
  ifstream infile(ddf);
  if(!infile.is_open()) err(str("failed to open file") + ddf);

  str line("");
  vector<int> start;
  vector<int> stop;
  vector<int> length;
  vector<str> label;
  vector<str>::iterator it;
  register long unsigned int ci = 0;

  /* process file line by line */
  while(getline(infile, line)){
    ci +=1;
    vector<str> w(split(line, ','));
    for(it = w.begin(); it != w.end(); it++){
      strip(*it);
      std::transform(it->begin(), it->end(), it->begin(), ::tolower); // to lower case
    }
    if(ci==1){
      if(w[0] != str("start")) err(str("expected field 0 ") + w[0]);
      if(w[1] != str("stop")) err(str("expected field 1 ") + w[1]);
      if(w[2] != str("length")) err(str("expected field 2 ") + w[2]);
      if(w[3] != str("label") && w[3] != str("name abbrev")) err(str("expected field 3 ") + w[3]);
    }
    else{
      start.push_back(atoi(w[0].c_str()));
      stop.push_back(atoi(w[1].c_str()));
      length.push_back(atoi(w[2].c_str()));
      label.push_back(w[3]);
      if(atoi(w[1].c_str()) + 1 - atoi(w[0].c_str()) != atoi(w[2].c_str())){
        err("length mismatch error");
      }
    }
  }

  cout << start << endl << stop << endl << length << endl << label << endl;
  cout << "applying data dictionary.." << endl;

  ifstream dfile(dtf);
  if(!dfile.is_open()) err(str("failed to open input data file:") + dtf);

  long unsigned int dfile_pos;
  dfile.seekg (0, dfile.end);
  long unsigned int dfile_len = dfile.tellg();
  dfile.seekg (0, dfile.beg);

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(str("failed to write-open file:") + ofn);

  /* linefeed not a thing */
  if(label.back() == str("LINEFEED")) label.pop_back();

  outfile << join(",", label) << "\n";

  str d;
  ci = 0;
  unsigned int i;
  unsigned int ul = label.size();
  vector<str> row;
  time_t t0; time(&t0);
  time_t t1;

  while(getline(dfile, line)){
    ci += 1;
    if(ci % 100000 == 0){
      dfile_pos = dfile.tellg();
      time(&t1);
      time_t dt = t1-t0;
      float mbps = (float)dfile_pos / ((float)dt * (float)1000000.);
      float eta = (float)dt * ((float)dfile_len - (float)dfile_pos) / ((float)dfile_pos);
      float p = 100. * (float)dfile_pos / (float) dfile_len;
      cout << "ddap %" << p << " eta: " << eta << "s MB/s " << mbps << endl;
    }
    row.clear();
    for(i = 0; i < ul; i++){
      d = line.substr(start[i] - 1, length[i]);
      strip(d);
      replace(d.begin(), d.end(), ',', ';');
      row.push_back(d);
    }
    outfile << join(",", row) + str("\n");
    outfile.flush();
  }
  return 0;
}
