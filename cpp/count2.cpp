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

/* 20190429 count.cpp: count occurence of different codes
output one hist per file!!! */
#include"misc.h"
using namespace std;

int main(int argc, char ** argv){
  int i, j;
  if(argc < 2) err("usage: count.cpp [input file]");

  str fn(argv[1]);
  str ofn(fn + string("_count"));
  cout << "data output file: " << ofn << endl;

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);
  str line;

  time_t t0; time(&t0); time_t t1;

  string d;
  vector<str> words;
  ifstream dfile(fn);
  long unsigned int infile_pos;
  dfile.seekg (0, dfile.end);
  long unsigned int infile_len = dfile.tellg();
  dfile.seekg (0, dfile.beg);

  getline(dfile, line);
  vector<str> fields = split(line);
  int n_fields =fields.size();

  map<str, unsigned long int> counts;
  unsigned int ci = 0;
  while(getline(dfile, line)){
    words = split(line, ',');
    for(vector<str>::iterator it = words.begin(); it != words.end(); it++){
      str i = *it;
      if(counts.count(i) < 1) counts[i] = 1;
      counts[i] += 1;
    }
    if(++ci % 100000 == 0){
      size_t infile_pos = dfile.tellg();
      time(&t1);
      time_t dt = t1-t0;
      float mbps = (float)infile_pos / ((float)dt * (float)1000000.);
      float eta = (float)dt * ((float)infile_len - (float)infile_pos) / ((float)infile_pos);
      float p = 100. * (float)infile_pos / (float) infile_len;
      cout << "count %" << p << " eta: " << eta << "s MB/s " << mbps << endl;
    }
  }
  dfile.close();
  cout << "writing.." << endl;
  ci = 0;
  float len = (float) counts.size();
  for(map<str, unsigned long int>::iterator it = counts.begin(); it != counts.end(); it++){
    outfile << it->first << "," << it->second <<endl;
    if(ci ++ % 10000 == 0){
      cout << 100. * (float)ci / len << endl;
    }
  }
  outfile.close();
  return 0;
}
