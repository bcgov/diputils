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
/* 20190212 deselect.cpp: remove records where FIELD=value1 or FIELD=value2.. etc
e.g., csv_deselect.exe idomed*schlstud.a.dat_slice.csv special_need_code_this_coll "NON SPECIAL NEED" */
#include"misc.h"
using namespace std;

// note: this needs to be updated to partition the data into two files: accepted and rejected

int main(int argc, char ** argv){
  printf("note: this program detects and removes double quote signs around fields.\n");

  if(argc < 4) err("usage: deselect.cpp [input file] [field name] [value1] .. [valuen]");

  string dfn(argv[1]);
  string fn(argv[2]);
  string ofn(dfn + str("_deselect-incl.csv"));
  string of2(dfn + str("_deselect-excl.csv"));

  vector<string> value;

  cout << "deselecting field: " << fn << endl;
  for(int i = 3; i < argc; i++){
    string v(argv[i]);
    /* remove quotation marks from the field name, if they're there.. */
    if(v[0] == '"') v.erase(0);
    if(v[v.size()-1] == '"') v.erase(v.size()-1);
    value.push_back(v);
    cout << "deselecting value: '" << v << "'" << endl;
  }

  cout << "input file: " << dfn << endl;
  cout << "output file: " << ofn << endl;
  cout << "output file: " << of2 << endl;

  ifstream dfile(dfn);
  if(!dfile.is_open()) err(string("failed to open input data file:") + dfn);

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);

  ofstream outfil2(of2);
  if(!outfil2.is_open()) err(string("failed to write-open file:") + of2);

  string d;
  string line;
  vector<string> row;
  unsigned int selecti;
  long unsigned int ci = 0;
  bool selected = false;

  /* for each line in the file */
  while(getline(dfile, line)){
    row = split(line, ',');
    if(ci == 0){
      unsigned int si = 0;
      for(vector<string>::iterator it = row.begin(); it != row.end(); it++){
        if(*it == fn){
          selecti = si;
          selected = true;
        }
        si++;
      }
      if(!selected){
        err("field not selected");
      }
      /* write out the header file */
      outfile << line << endl;
      outfil2 << line << endl;
    }
    else{
      selected = true;
      for(vector<string>::iterator it = value.begin(); it != value.end(); it++){
        string itt(*it);
        trim(itt);
        trim(row[selecti]);
        if(row[selecti] == itt) selected = false;
      }
      if(selected) outfile << line << endl;
      else outfil2 << line << endl;
    }
    ci ++;
  }
  dfile.close();
  outfile.close();
  outfil2.close();
  return 0;
}
