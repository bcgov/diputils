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
/* 20190312 csv_lookup: apply a lookup table (two cols) to a csv file
  parameters:

    [lookup file: two cols: input (to match), output (to be assigned to match]
    [input data file]

  Note: the col. to match on, must be present in the input data

  The output will match the input, with an additional col. inserted.. for the lookup value */
#include"misc.h"

// when matching studyid, have to check if there is an "S" in front!!!!! Or not!!!

int main(int argc, char ** argv){
  if(argc < 3) err("usage: csv_lookup [lookup file] [file to apply lookup to]");
  cout << "Opening file: " << argv[1] << endl;
  mfile l_f(string(argv[1]), "rb"); // if this was too big to keep in mem, could use rewind() to re-scan it
  cout << "Opening file: " << argv[2] << endl;
  mfile d_f(string(argv[2]), "rb"); // data file..

  unsigned int i;
  string s;
  map<str, str> lookup;
  vector<string> words;
  long unsigned int l_i = 0;

  // read header from lookup file (should be two cols)
  l_f.getline(s);
  words = split(s);
  if(words.size() != 2) err("lookup file should have two fields");

  str map_in(words[0]);
  str map_out(words[1]);

  cout << "creating lookup table.." << endl;
  while(l_f.getline(s)){
    words = split(s);
    if(words.size() != 2){
      err("two fields expected");
    }
    trim(words[0]);
    trim(words[1]);
    lower(words[0]);
    lower(words[1]);

    lookup[words[0]] = words[1];
    if((++ l_i) % 10000 == 0){
      l_f.status();
      cout << endl; //cout << words << " " << words[s_f_i] << endl;
      cout.flush();
    }
  }
  l_f.close(); // free up the memory

  bool found = false;
  unsigned int map_field_i;
  d_f.getline(s);
  vector<string> fields = split(s);
  cout << fields << endl;
  for0(i, fields.size()){
    if(fields[i] == map_in){
      map_field_i = i;
      found = true;
    }
  }
  if(!found) err("could not find map field in data file");

  FILE * f = wopen((string(argv[2]) + "_lookup.csv").c_str());
  if(!f) err("failed to open output file");

  FILE * g = wopen((string(argv[2]) + "_lookup-fail.csv").c_str());
  if(!g) err("failed to open output file");

  for0(i, fields.size()){
    if(i > 0) fprintf(f, ",");

    fprintf(f, "%s", fields[i].c_str());
    if(i == map_field_i) fprintf(f, ",%s", map_out.c_str());
  }
  fprintf(f, "\n");

  l_i = 0;
  long unsigned int count_na = 0;
  long unsigned int count_total = 0;
  while(d_f.getline(s)){
    words = split(s);
    for(i = 0; i < words.size(); i++){
      trim(words[i]);
      lower(words[i]);
    }

    str outs("");
    for0(i, words.size()){
      if(i > 0) fprintf(f, ",");
      fprintf(f, "%s", words[i].c_str());
      if(i == map_field_i){
        if(lookup.count(words[i]) > 0){
          fprintf(f, ",%s", lookup[words[i]].c_str());
          count_total ++;
        }
        else{
          fprintf(f, ",N/A");
          count_na ++;
          cout << words << endl;
          fprintf(g, "%s\n", s.c_str());
        }
      }
    }
    fprintf(f, "\n");
    if((++ l_i) % 100000 == 0){
      d_f.status();
      cout << endl; //cout << words << " " << words[s_f_i] << endl;
      cout.flush();
    }
  }
  fclose(f);
  fclose(g);
  cout << "Number of elements that failed to be mapped: " << count_na << " of total: " << (count_total + count_na)<< endl;
  return 0;
}
