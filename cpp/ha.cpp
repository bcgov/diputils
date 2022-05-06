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
/* for version-control applications, append data to file */
#include<string>
#include<stdio.h>
#include<fstream>
#include<stdlib.h>
#include<iostream>
using namespace std;
void er(string s){
  cout << "Error: " << s << endl; exit(1);
}
int main(int argc, char ** argv){
  string fn("");
  string dat("");
  string fnf_fn("./.ha");
  string fnf_fd("./.ha_d");
  FILE * g = NULL;

  if(argc == 3){
    fn = string(argv[1]);
    dat = string(argv[2]);
    ofstream f(fnf_fn); f << fn; f.close();
    g = fopen(fn.c_str(), "wb");
  }
  else if(argc == 2){
    dat = string(argv[1]);
    ifstream f(fnf_fn); f >> fn; f.close();
    g = fopen(fn.c_str(), "ab");
  }
  else er("usage: ha [input file]");
  if(!g) er("failed to open file for writing");
  if(dat.size() %2 != 0) er("data size not div. by two");

  if(true){
    ofstream f(fnf_fd); f << dat; f.close();
  }

  unsigned char c, d;
  FILE * f = fopen(fnf_fd.c_str(), "rb");
  while(fscanf(f, "%02hhX", &c) != EOF) fprintf(g, "%c", c);
  fclose(f);
  fclose(g);

  if(true){
    ofstream f(fnf_fd); f << ""; f.close();
  }
  return 0;
}
