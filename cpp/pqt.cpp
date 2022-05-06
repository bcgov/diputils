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

#include<map>
#include<cmath>
#include"misc.h"
#include<fstream>
#include<stdio.h>
#include<iostream>
#include<stdlib.h>
#include<stdint.h>
using namespace std;
/* pqt.cpp:
This is a conversion to a columnar data type with
 - dictionary encoding
 - bit packing
 
 Unlike Apache parquet it does not include run-length encoding*/


/* extract the field name produced by csv_split */
str fieldname_from_filename(str fn){
  vector<str> w(split(fn, '_'));
  int j = 0;
  int csv_i = -1;
  for(vector<str>::iterator it = w.begin(); it != w.end(); it++){
    string s(*it);
    int s_len = s.size();
    if(s[s_len - 1] == 'v' && s[s_len - 2] == 's' && s[s_len - 3] == 'c') csv_i = j;
    j++;
  }
  int k;
  vector<str> ans;
  for(k = csv_i + 1; k < w.size(); k++) ans.push_back(w[k]);
  const char * d = "_\0";
  return join(d, ans);
}

int main(int argc, char ** argv){
  if(argc < 2){
    err("usage: encode [csv file, 1 col, with header]");
  }
  string fn(argv[1]);

  // assert that col header matches end of filename
  string field_name(fieldname_from_filename(fn));
  trim(field_name);
  lower(field_name);

  str s;
  vector<str> words;
  vector<set<str>> c;
  long unsigned int nrow = 0;

  str o_fn(fn + str(".pqt"));
  cout << "output file: " << o_fn << endl;
  FILE * g = fopen(o_fn.c_str(), "wb");
  if(!g) err("failed to open output file");

  ifstream f(fn);
  long unsigned int dfile_pos, dfile_len;
  f.seekg(0, f.end);
  dfile_len = f.tellg();
  f.seekg(0, f.beg);

  getline(f, s);
  trim(s);
  lower(s);

  std::replace(s.begin(), s.end(), '.', '_');
  // assert that col header matches end of filename (i.e., was produced by csv_split)
  if(s != field_name) err("field name: " + s + " (from header) didn't match field name: " + field_name + " (from filename)");

  set<str> dat;
  while(getline(f,s)){
    trim(s);
    dat.insert(s);
  }

  cout << "number of unique elements: " << dat.size() << endl;
  int nbytes = (int) ceil(log((float)(dat.size() + 1)) / log(pow(2., 8.)));
  cout << "number of bytes required: " << nbytes << endl;

  rewind(f); // rewind, next pass
  getline(f,s); // read header again

  unsigned int next_idx = 0;
  map<str, unsigned int> idx;
  map<unsigned int, str> xdi;

  cout << "second read pass.." << endl;
  register unsigned int k;
  unsigned int largest = 1;
  register unsigned int div;
  for0(k, nbytes - 1) largest *= 256; // pow(2,8) = 256

  unsigned char * dd = (unsigned char *) (void *)balloc(nbytes);
  while(getline(f, s)){
    trim(s);
    for(k = 0; k < s.size(); k++) if(s[k] == ',') err("expected single-col csv");

    if(idx.count(s) == 0){
      idx[s] = next_idx;
      xdi[next_idx++] = s;
    }

    unsigned int d = idx[s];

    div = largest;
    unsigned int remain, result;
    remain = d;
    for0(k, nbytes - 1){
      result = d / div;
      remain = d % div;
      if(result > 255) err("result bigger than 255");
      dd[k] = (unsigned char) result;
      div /= 256;
      d = remain;
    }

    if(remain > 255){
      cout << "remain: " << remain << endl;
      err("remain > 255");
    }
    dd[nbytes - 1] = (unsigned char) remain;
    fwrite(&dd[0], sizeof(unsigned char), nbytes, g);

    if((++nrow) % 1000000 == 0){
      dfile_pos = f.tellg();
      cout << "%" << 100. * (float)dfile_pos / (float) dfile_len << endl;
    }
  }

  for0(k, next_idx) fprintf(g, "\n%s", xdi[k].c_str());

  // footer
  fprintf(g, "\nnbyte,%d", (int)nbytes);
  fprintf(g, "\nnxt_i,%d", (int)next_idx);
  fprintf(g, "\nn_row,%d", (int)nrow);

  cout << "encoded elements: " << nrow << endl;
  fclose(g);
  f.close();
  free(dd);
  return 0;
}
