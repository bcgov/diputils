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
/* for version-control appl'n: convert to hex:
Generate hexdiffs so we can examine special characters, etc. */
int main(int argc, char ** argv){
  str fn;
  str fnf_fn("./.b2h");
  str fnf_fnp(fnf_fn + str("p"));

  unsigned char c;
  const char * f_n;
  size_t i = 0;
  size_t f_p = 0;

  if(argc > 1){
    f_n, fn = argv[1], str(argv[1]);
    ofstream f(fnf_fn); f << fn; f.close();
    ofstream g(fnf_fnp); g << 0; g.close();
  }
  else{
    ifstream g(fnf_fnp); g >> f_p; g.close();
  }

  if(fsize(fnf_fn) == (size_t)0) err("b2h [file name]");
  ifstream fnf(fnf_fn); fnf >> fn; fnf.close();
  f_n = fn.c_str();

  FILE * f = fopen(f_n, "rb");
  if(!f) err(str("failed to open file: ") + str(f_n));
  size_t f_s = size(f);

  if(f_p >= f_s - 1){
    system((str("rm -f ") + fnf_fn).c_str());
    system((str("rm -f ") + fnf_fnp).c_str());
    exit(0);
  }
  printf("%s%d%s\n\n ", KNRM, f_p, KGRN);
  unsigned long int l_i, c_i;
  l_i = c_i = 0;
  fseek(f, f_p, SEEK_SET);
  for(i = f_p; i < f_s; i++){
    c = fgetc(f);
    printf("%.2X", (unsigned char)c);
    if(++c_i % 32 == 0){
      if(++ l_i > 32) break;
      printf("\n ");
    }
  }
  ofstream g(fnf_fnp);
  g << string(to_string(++i));
  g.close();
  printf("\n\n%s%d\n", KNRM, i);
  return 0;
}
