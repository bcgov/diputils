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

/* 20190319 dd_slice_apply.cpp:
 * use data dictionary to translate from from fixed-width to csv,
 however, retaining only desired col's!!!!!! */
#include"misc.h"
#include<ctime>
#include<vector>
#include<string>
#include<fstream>
#include<iostream>
#include<algorithm>
using namespace std;

int main(int argc, char ** argv){
  if(argc < 4) err("usage: dd_slice_apply.cpp [data dictionary.csv] [data input.dat] [desired field 1] [desired field 2]... [desired field n]");

  register unsigned int i;
  str ddf(argv[1]);
  str dtf(argv[2]);
  vector<str> desf;
  vector<str>::iterator it;
  str ofn(dtf + str("_dd_sliceapply.csv"));

  for(i = 3; i < argc; i++) desf.push_back(str(argv[i]));
  for(it = desf.begin(); it != desf.end(); it++) lower(*it);

  cout << "data dictionary file: " << ddf << endl;
  cout << "data input file: " << dtf << endl;
  cout << "output file: " << ofn << endl;
  cout << "desired fields:" << desf << endl;

  ifstream infile(ddf);
  if(!infile.is_open()) err(str("failed to open file") + ddf);

  str line("");
  vector<str> label;
  vector<int> start, stop, length;
  map<str, unsigned int> label_lookup;
  map<unsigned int, str> lookup_label;
  register long unsigned int ci = 0;

  /* process data dictionary line by line */
  while(getline(infile, line)){
    vector<str> w(split(line, ','));
    for(it = w.begin(); it != w.end(); it++){
      lower(*it);
      strip(*it);
    }
    if(ci==0){
      vector<str> rf; // req'd fields
      rf.push_back(str("start"));
      rf.push_back(str("stop"));
      rf.push_back(str("length"));
      rf.push_back(str("label"));
      int i;
      for0(i, 4) if(w[i] != rf[i]){
        if(i != 3 && w[i] != "name abbrev"){
          err(str("req'd field:") + w[i]);
        }
      }
    }
    else{
      start.push_back(atoi(w[0].c_str()));
      stop.push_back(atoi(w[1].c_str()));
      length.push_back(atoi(w[2].c_str()));
      label.push_back(w[3]);
      label_lookup[w[3]] = ci - 1; // field index: field line number less one
      if(atoi(w[1].c_str()) + 1 - atoi(w[0].c_str()) != atoi(w[2].c_str())){
        cout <<w << endl;
        err("length mismatch error");
      }
    }
    ci ++;
  }
  cout << "labels: " << label << endl;

  /* check that provided fields are present and make a look-up */
  set<str> labels;
  for(it = label.begin(); it != label.end(); it++) labels.insert(str(*it));

  /* desired fields (use set to find non-redundant) */
  set<str> desfs;
  for(it = desf.begin(); it != desf.end(); it++){
    desfs.insert(*it);
    if(labels.count(*it) < 1){
      cout << "\nlabels";
      set<str>::iterator it2;
      for(it2 = labels.begin(); it2 != labels.end(); it2++){
        cout << "," << *it;
      }
      cout << endl;
      err(str("field not found in data dictionary: ") + *it);
    }
  }

  /* linefeed not a thing */
  if(label.back() == str("LINEFEED")) label.pop_back();

  cout << "start" << start << endl << "stop" << stop << endl << "length" << length << endl << label << endl;
  unsigned int total_len = 0;
  for(vector<int>::iterator it = length.begin(); it != length.end(); it++){
    total_len += *it;
  }
  cout << "total length: " << total_len << endl;

  cout << "applying data dictionary.." << endl;

  ifstream dfile(dtf);
  if(!dfile.is_open()) err(str("failed to open input data file:") + dtf);

  /* calculate file size */
  long unsigned int dfile_pos, dfile_len, dfile_pos_last;
  dfile.seekg(0, dfile.end);
  dfile_len = dfile.tellg();
  dfile.seekg(0, dfile.beg);

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(str("failed to write-open file:") + ofn);

  unsigned int n_f = desfs.size();
  unsigned int * dstart = (unsigned int *) balloc(sizeof(unsigned int) * n_f);
  unsigned int * dlength= (unsigned int *) balloc(sizeof(unsigned int) * n_f);

  ci = 0;
  for(it = label.begin(); it != label.end(); it++){
    if(desfs.count(*it) > 0){
      dstart[ci] = start[label_lookup[*it]];
      dlength[ci]= length[label_lookup[*it]];
      lookup_label[ci] = *it;
      ci ++;
    }
  }
  outfile << lookup_label[0];
  for0(ci, n_f -1) outfile << "," << lookup_label[ci + 1];

  str d;
  ci = 0;
  vector<str> row;
  time_t t0, t1; time(&t0);

  /* multithreaded chunking? */
  while(getline(dfile, line)){
    for0(i, n_f){
      d = line.substr(dstart[i] - 1, dlength[i]);
      strip(d);
      std::replace(d.begin(), d.end(), ',', ';');
      row.push_back(d);
    }
    outfile << str("\n") + join(",", row);
    if(++ci % 100000 == 0){
      time(&t1);
      time_t dt = t1-t0;
      dfile_pos = dfile.tellg();
      float p = 100. * (float)dfile_pos / (float) dfile_len;
      float mbps = (float)(dfile_pos)/ ((float)dt * (float)(1024*1024));// * (float)1000000.);
      float eta = (float)dt * ((float)dfile_len - (float)dfile_pos) / ((float)dfile_pos);
      cout << "ddsa %" << p << " eta: " << eta << "s MB/s " << mbps << endl; // " dt=" << dt << endl;
      dfile_pos_last = dfile_pos;
    }
    row.clear();
  }
  cout << "exit" << endl;

  free(dstart);
  free(dlength);

  ofstream rc;
  rc.open(dtf + str(".rc"));
  if(!rc.is_open()) err(str("failed to open .rc file"));
  rc << "n_records_sliced,n_records_total" << endl;
  rc << ci << "," << ci << endl;
  rc.close();
  return 0;
}
