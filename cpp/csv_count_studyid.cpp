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
/* 20190724: should update this program to identify the studyid col
 20220506 this program is probably deprecated by unique.cpp */
int main(int argc, char** argv){
  if(argc < 2) err("count_studyid.cpp: usage: count_studyid [input file, csv, last col STUDYID");
  string fn(argv[1]);
  cout << "input file: " << fn << endl;

  ifstream infile(fn);
  if(!infile.is_open()) err(string("failed to open input file: ") + fn);

  string line;
  string studyid;
  long unsigned int ci = 0;

  map<string, long unsigned int> count;
  count.clear();

  long unsigned int nf = 0;
  while(getline(infile, line)){
    vector<string> w(split(line, ','));
    for(vector<string>::iterator it = w.begin(); it != w.end(); it++) trim(*it);
    if(ci == 0){
      nf = w.size();
      if(w[nf - 1] != "STUDYID" && w[nf - 1] != "study-id" && w[nf - 1] != "studyid"){
        err("expected last field studyid or STUDYID");
      }
    }
    else{
      if(w.size() != nf){
        cout << "line : " << ci << endl;
        err("field count mismatch");
      }
      studyid = w[nf - 1];
      map<string, long unsigned int>::iterator it = count.find(studyid);
      if(it == count.end()) count[studyid] = 0;
      count[studyid] += 1;
    }
    ci += 1;
  }

  cout << "Unique studyid: " << count.size() << endl;

  map<long unsigned int, long unsigned int> cc;
  for(map<string, long unsigned int>::iterator it = count.begin(); it != count.end(); it++){
    long unsigned int cci = it->second;
    map<long unsigned int, long unsigned int>::iterator cit = cc.find(cci);
    if(cit == cc.end()) cc[cci] = 0;
    cc[cci] += 1;
  }

  cout << "count of studyid counts: " << cc << endl;
  return 0;
}
