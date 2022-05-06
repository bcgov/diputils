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

#include"misc.h"
/* 20190909 csv_sort.cpp:
low-memory sort (numeric field). 
User must select field to sort on !!!

This software is required to deal with resource limitations in SRE */

/* sort_idx: 
 * for sorting: numeric value from sort field, plus record's memory location (in-file) */
class sort_idx{
  public:
  float d;
  size_t idx;
  sort_idx(float d_, size_t i){
    d = d_;
    idx = i;
  }
  sort_idx(const sort_idx &a){
    d = a.d;
    idx = a.idx;
  }
};

bool operator<(const sort_idx& a, const sort_idx&b){
  return a.d < b.d; // priority_queue is max first, need to switch direction for min first
}

int main(int argc, char** argv){

  priority_queue<sort_idx> queue;

  if(argc < 2) err("csv_sort [input file csv] [field name to sort on]; # assumes field is numeric\n");

  str s(""); // line buffer
  size_t last_p; // last file location read
  str fn(argv[1]); // input file
  str sort_field_name(argv[2]); // numeric field name to sort on
  str ofn(fn + "_sort.csv"); // output file

  if(argc > 3){
    ofn = str(argv[3]);
  }

  cout << "output file: " << ofn << endl;

  size_t f_size = fsize(fn); // size of input file
  ifstream f(fn); // open the input file
  long unsigned int l_i = 0; // row count for progress bar
  if(!f.is_open())err("failed to open input file");

  ofstream of(ofn); // open output file
  if(!of.is_open()) err(str("failed to open output file: ") + ofn);

  last_p = f.tellg();
  getline(f, s);
  of << s; // write header to output file
  l_i += 1;

  trim(s); // format field data
  lower(s); // convert to lower case
  vector<str> w(split(s)); // split on comma by default
  int n_f = w.size(); // count the number of fields

  cout << "fields: " << w << endl;

  map<str, int> f_i; // map the field name to index
  for(int k = 0; k < w.size(); k++){
    f_i[w[k]] = k;
  }

  int sort_field = -1;
  if(f_i.count(sort_field_name) < 1) err("couldn't find requested sort field in input file");
  sort_field = f_i[sort_field_name];

  cout << "sort field index: " << sort_field << endl;

  last_p = f.tellg(); // file location data value was extracted from
  while(getline(f, s)){
    trim(s);
    lower(s);
    w = split(s);
    if(w.size() != n_f){
      cout << "line number: " << l_i << endl;
      cout << "data: " << w << endl;
      err("unexpected number of fields");
    }

    float d = atof(w[sort_field].c_str());
    queue.push(sort_idx(d, last_p));
    // cout << "push " << d << " " << last_p << endl;
    l_i += 1; // row count for progress indicator
    last_p = f.tellg();

    if(l_i % 1000000 == 0){
      cout << "%" << 100. * float(last_p) / float(f_size) << endl;
    }
  }

  f.clear();
  f.seekg(0, ios::beg); // rewind the file

  while(!queue.empty()){
    last_p = queue.top().idx;
    queue.pop();

    f.seekg(last_p);
    if(!getline(f, s)){
      cout << "file position (bytes): " << last_p << endl;
      err("failed getline");
    }
    //don't leave newline at very end
    of << endl << s;
  }
  f.close();
  return 0;
}
