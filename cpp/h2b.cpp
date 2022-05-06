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

/* for version-control applications, convert hex to uchar */
#include<stdio.h>
#include<stdlib.h>
#include<string>
#include<iostream>
using namespace std;
void er(string s){
  cout << "Error: " << s << endl; exit(1);
}
/* for version-control applications, convert hex to char */
int main(int argc, char ** argv){
  if(argc < 2) er("usage: h2b [input file]");
  unsigned char c, d;
  FILE * f = fopen(argv[1], "rb");
  if(!f) er(string("failed to open input file: ") + string(argv[1]));
  FILE * g = fopen( (string(argv[1]) + string(".b")).c_str(), "wb");
  while(fscanf(f, "%02hhX", &c) != EOF) fprintf(g, "%c", c);
  fclose(f);
  fclose(g);
  return 0;
}