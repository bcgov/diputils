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

/* 20190304 csv cat: assert headers match and cat the rest of the file */
#include"misc.h"
using namespace std;

int main(int argc, char ** argv){
  int i, j;
  if(argc < 2) err("usage: csv_cat.cpp [input file] .. [input file n]");

  vector<string> filenames;
  for(i = 1; i < argc; i++) filenames.push_back(string(argv[i]));

  int bad_header = false;
  string header0;
  for(i = 0; i < filenames.size(); i++){
    string header;
    /* check all the files actually open before we go ahead.. getting partway through the job would suck*/
    ifstream dfile(filenames[i]);
    getline(dfile, header);
    trim(header);
    if(i == 0) header0 = header;
    if(header0 != header){
      cout << "error: file :" << filenames[i] << " header:\n\t" << header << " didn't match first header: \n\t" << header0 << endl;
      bad_header = true;
    }

    if(!dfile.is_open()) err(string("failed to open input data file:") + filenames[i]);
    dfile.close();
  }
  if(bad_header) return 1;

  str ofn(string("csv_cat.csv"));
  cout << "data output file: " << ofn << endl;

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);

  str line;

  time_t t0; time(&t0); time_t t1;
  long unsigned int l_i = 0; // row index of output
  long unsigned int c_i = 0;

  string d;
  for(j = 0; j < filenames.size(); j++){
    cout << "data input file: " << filenames[j] << endl;
    ifstream dfile(filenames[j]);

    // read header and output only if it's the first one..
    getline(dfile, line);
    if(l_i ++ == 0) outfile << line << endl;
    while(getline(dfile, line)){
      outfile << line << endl;
      l_i ++;
    }
    dfile.close();
  }
  cout << "writing.." << endl;
  outfile.close();
  return 0;
}
