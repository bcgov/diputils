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
/* blind paste of csv's left to right (insert comma between files)
Useful if used with caution! */
#include"misc.h"
int main(int argc, char ** argv){
  if(argc < 3){
    err("csv_unsplit [input file 1] .. [input file n]\n\tinput files are 1-col csv's of same length");
  }
  int i;
  int n_files = argc - 1;
  ifstream f[n_files];
  for0(i, n_files){
    cout << "fopen " << argv[i + 1] << endl;
    f[i].open(argv[i + 1]);
  }
  for0(i, n_files) if(!f[i].is_open()) err("failed to open input file");

  ofstream g("csv_unsplit.csv");
  str s;
  str comma(",");
  while(getline(f[0], s)){
    //trim(s);
    g << s;
    for0(i, n_files - 1){
      getline(f[i + 1], s);
      //trim(s);
      g << comma << s;
    }
    g << std::endl;
  }

  g.close();
  for0(i, n_files) f[i].close();
  free(f);
  return 0;
}
