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
/* More detailed metric on counts of outcomes:
this version is for a single-column (columnar) dataset */
#include"misc.h"
class sort_idx{
  // index / count tuple to sort counts
  public:
  str data;
  long unsigned int count;
  sort_idx(str a_data = str(""), long unsigned int a_count = 0){
    data = a_data;
    count = a_count;
  }
  sort_idx(const sort_idx& a){
    data = a.data;
    count = a.count;
  }
};

bool operator< (const sort_idx& a, const sort_idx& b){
  return a.count < b.count;
}

int main(int argc, char ** argv){
  if(argc < 2) err("count_col [input 1-col csv data file, incl. header]");
  str s;
  ifstream f;
  ofstream g;
  str fn(argv[1]);
  str ofn(fn + "_count.csv");

  f.open(fn);
  g.open(ofn);
  size_t p, f_size;
  cout.precision(3);
  f_size = fsize(fn);
  float denom = (float)(1024 * 1024);
  if(!g.is_open()) err(str("failed to open output file") + ofn);
  if(!f.is_open()) err(str("failed to open input file: ") + str(argv[1]));
  cout << "counting events from input file: " << fn << " size (bytes): " << f_size << endl;

  getline(f, s); // header
  size_t last_p = 0;
  long unsigned int ci = 0;
  map<str, unsigned int> count;
  while(getline(f, s)){
    if(count.count(s) < 1) count[s] = 1;
    else count[s] += 1;

    if(++ci % 10000000 == 0){
      p = f.tellg();
      float prcnt_scan = 100. * (float)p / (float)f_size;
      float mb_per_sec = ((float)p - (float)last_p) / denom;
      cout << "%" << prcnt_scan << " " << ((last_p > 0 )? mb_per_sec: 0.) << " MB/s" << endl;
      last_p = p;
    }
  }
  f.close();
  sort_idx top;
  long unsigned int c, m;
  float freq_percent_cumul = 0.;
  float mass_percent_cumul = 0.;
  float freq_percent, mass_percent;
  long unsigned int total_mass = 0;
  long unsigned int total_count = 0;
  long unsigned int n_records = ci + 1;

  cout << "sorting.." << endl;
  priority_queue<sort_idx> list;
  for(map<str, unsigned int>::iterator it = count.begin(); it != count.end(); it++){
    total_count += it->second;
    list.push(sort_idx(it->first, it->second));
    total_mass += atol((it->first).c_str()) * (it->second);
  }

  g << "term,count,freq_prcnt,freq_prcnt_cumul,mass_prcnt,mass_prcnt_cumul";
  while(list.size() > 0){
    top = list.top();
    s = top.data;
    c = top.count;
    m = atol(s.c_str()) * c; //list.top().count;
    freq_percent = 100. * (float)c / (float) total_count;
    mass_percent = 100. * (float)m / (float) total_mass;
    freq_percent_cumul += freq_percent;
    mass_percent_cumul += mass_percent;
    g << endl << s << "," << c << ","; // data, count,
    g << freq_percent << "," << freq_percent_cumul << ","; // freq_prcnt,freq_prcnt_cumul,
    g << mass_percent << "," << mass_percent_cumul; // mass_prcnt,mass_prcnt_cumul
    list.pop(); // next element
  }
  g.close();
  return 0;
}
