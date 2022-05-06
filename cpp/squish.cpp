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

/* 20190212 merge: assuming second/last field is studyid,
 * calculate mode of other field */
#include"misc.h"
using namespace std;

int main(int argc, char ** argv){
  cout << argc << endl;
  if(argc < 2) err("usage: squish [input file: csv, 2 cols] # mode-flattening for csv file (note: homoiconic property: comments and doc in here should be the same..");

  string fn(argv[1]);
  string ofn(fn + string("_merge.csv"));
  cout << "data input file: " << fn << endl;
  cout << "data output file: " << ofn << endl;

  ifstream dfile(fn);
  if(!dfile.is_open()) err(string("failed to open input data file:") + fn);

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);

  string line;
  string code;
  string studyid;
  vector<string> row;
  long unsigned int ci = 0;
  map<string, map<string, long unsigned int>> count;

  while(getline(dfile, line)){
    row = split(line, ',');
    for(vector<string>::iterator it = row.begin(); it != row.end(); it++) strip(*it);

    if(ci == 0){
      if(row.size() != 2) err("two fields expected");
      string last(row[row.size()-1]);
      if(last != string("STUDYID") && last != string("study-id")){
        err("expected STUDYID or study-id for last col. title");
      }
      outfile << line << endl;
    }
    else{
      code = row[0];
      studyid = row[row.size()-1];
      map<string, map<string, long unsigned int>>::iterator it = count.find(studyid);
      if(it == count.end()){
        /* initialize */
        count[studyid] = map<string, long unsigned int>();
        it = count.find(studyid);
        if(it == count.end()) err("failed to create key");

        map<string, long unsigned int>::iterator itt = count[studyid].find(code);
        if(itt == count[studyid].end()) count[studyid][code] = 0;
      }
      count[studyid][code] += 1;
    }
    ci ++;
  }

  for(map<string, map<string, long unsigned int>>::iterator it = count.begin(); it != count.end(); it++){
    /* for each studyid */
    studyid = it->first;
    map<string, long unsigned int> c(it->second);
    string maxs("");
    long unsigned int maxv = 0;
    for(map<string, long unsigned int>::iterator itt = c.begin(); itt != c.end(); itt++){
      if(itt->second >= maxv){
        maxs = itt->first;
        maxv = itt->second;
      }
    }
    /* output the most frequent label, if there was one.. */
    outfile << maxs << "," << studyid << endl;
  }

  dfile.close();
  outfile.close();
  return 0;
}
