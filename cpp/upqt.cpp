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
/* inverse operation of pqt.cpp!!!!!!!  */
#include<map>
#include<stack>
#include<cmath>
#include"misc.h"
#include<fstream>
#include<stdio.h>
#include<iostream>
#include<stdlib.h>
#include<stdint.h>
#define MAXCHAR (1024*1024)
using namespace std;

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
  if(argc < 2) err("usage: unencode [.csv_*.pqt file ]");
  string fn(argv[1]);

  str ext(fn.substr(fn.size() -4, fn.size() - 1)); // pull the extension off the filename string
  if(ext != ".pqt") err(".pqt file required"); // pqt extension designates a compatible input

  string fn_base(fn.substr(0,fn.size()-4)); // filename less the extension
  string ofn(fn_base); // write back to original file name, assume not same place
  string field_name(fieldname_from_filename(fn_base));
  cout << "output file: " << fn_base << endl;

  FILE * g = fopen(ofn.c_str(), "wb");
  if(!g) err("failed to open output file");
  fprintf(g, "%s", field_name.c_str());

  str tmp_fn(fn + ".tmp");
  str cmd("tail -3 " + fn + " > " + tmp_fn);
  system(cmd.c_str());

  ifstream tf(tmp_fn);
  string s;

  getline(tf, s);
  vector<str> words0(split(s));
  if(words0[0] != "nbyte") err("expected field: nbyte");
  int nbyte = atoi(words0[1].c_str());

  getline(tf, s);
  vector<str> words1(split(s));
  if(words1[0] != "nxt_i") err("expected field: nxt_i");
  int nxt_i = atoi(words1[1].c_str());

  getline(tf, s);
  vector<str> words2(split(s));
  if(words2[0] != "n_row") err("expected field: n_row");
  int n_row = atoi(words2[1].c_str());

  cout << " nbyte=" << nbyte << " nxt_i=" << nxt_i << " n_row=" << n_row << endl;

  cmd = str("rm -f " + tmp_fn);
  system(cmd.c_str());

  FILE * f = fopen(fn.c_str(), "rb");
  if(!f) err("failed to open input file");

  unsigned char * d = (unsigned char *)(void *)balloc(n_row * nbyte);

  long unsigned int nr = fread(d, nbyte, n_row, f);
  cout << "first byte: " << (int)(unsigned char) d[0] << endl;
  if(nr != n_row) err("failed to read n_row lines");

  char buf[MAXCHAR];
  unsigned int i;
  fgets(buf, MAXCHAR, f); // one newline to get rid of

  map<unsigned int, str> xdi;

  for0(i, nxt_i){
    fgets(buf, MAXCHAR, f);
    string c(buf);
    trim(c);
    xdi[i] = c; // cout << "i=" << i << " xdi=" << xdi[i] << endl;
  }

  //now, output the codes to file: g
  stack<unsigned char> bytes;
  unsigned char * dp = d;
  register int k;
  for0(i, n_row){

    for0(k, nbyte){
      bytes.push(*dp); // cout << " * " << (int) bytes.top() << endl;
      dp++;
    }

    unsigned int value = 0;
    unsigned int multiplier = 1;

    for0(k, nbyte){
      unsigned char c = bytes.top();
      bytes.pop();
      value += ( ((unsigned int)c) * multiplier);
      multiplier *= 256;
      // cout << "value " << value << " multiplier " << multiplier << endl;
    }
    // cout << "value=" << value << " xdi[value]=" << xdi[value] << endl;
    fprintf(g, "\n%s", xdi[value].c_str());
  }
  free(d);
  fclose(g);
  fclose(f);
  return 0;
}
