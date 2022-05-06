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

//---------------------------------------------------------------------------//
// co_occur.cpp: co-occurence for multi-variate table
// date: 20190120
// info: input table given as cmd. arg: file assumed CSV: rows unique obs
//---------------------------------------------------------------------------//
#include<map>
#include<set>
#include"misc.h"
#include<vector>
#include<string>
#include<sstream>
#include<fstream>
#include<iostream>
#include"n_choose_m.h"
using namespace std;

/* statistical co-occurence */
std::map<std::string, long unsigned int> counts;

class count_idx{
  // date, file pointer tuple object
  public:
  str item;
  long unsigned int count;
  count_idx(str i = str(""), long unsigned int c = 0){
    item = i;
    count = c;
  }
  count_idx(const count_idx &a){
    item = a.item;
    count = a.count;
  }
};

bool operator<(const count_idx& a, const count_idx&b){
  return a.count < b.count; // priority_queue is max first
}

/* count string occurrences */
inline void incr(std::string label){
  if(counts.find(label) == counts.end()){
    counts[label] = 0;
  }
  counts[label] += 1;
}

int main(int argc, char ** argv){

  if(argc < 2){
    cout << "co_occur.cpp: default field selection: all" << endl;
    err("co_occur [input file.csv] [optional selected field 1] .. [optional selected field n]");
  }
  int i;
  int s_s = 3; // selection size;
  std::string filename(argv[1]);
  std::ifstream infile(filename);
  std::string line;

  long int ci = 0; // line count
  long int n_f = 0;
  vector<string> fields;

  set<string> select;
  if(argc >= 3){
    for(i = 2; i < argc; i++){
      select.insert(argv[i]);
    }
  }
  vector<int> select_i;

  /* process the file line by line */
  cout << "combinations:" << endl;
  vector<vector<int>> combs;
  vector<vector<int>>::iterator it;
  for(it= combs.begin(); it!=combs.end(); it++){
    cout << *it << endl;
  }

  getline(infile, line);
  std::vector<std::string> w(split(line, ','));
  fields = w;
  n_f = w.size();
  if(select.size() > 0){
    for0(i, n_f){
      if(select.count(fields[i]) > 0){
        select_i.push_back(i);
      }
    }
    combs = n_choose_up_to_m(select_i.size(), s_s);
  }
  else combs = n_choose_up_to_m(n_f, s_s);

  while(std::getline(infile, line)){
    w = split(line, ',');

    if(w.size() != n_f){
      cout << "Error: unexpected # of fields " << std::endl; return -1;
    }

    vector<string> w_f;
    if(select.size() > 0){
      for0(i, select_i.size()){
        w_f.push_back(w[select_i[i]]);
      }
    }
    else w_f = w;

    for(it = combs.begin(); it != combs.end(); it++){
      string s("");
      for(vector<int>::iterator ti = it->begin(); ti != it->end(); ti++){
        if(ti != it->begin()){
          s += string(",");
        }
        s += w_f[*ti];
      }
      incr(s);
    }
    ci += 1;
  }

  priority_queue<count_idx> pq;

  /* output string counts */
  for(std::map<std::string, unsigned long int>::iterator ti=counts.begin(); ti!=counts.end(); ti++){
    pq.push(count_idx(ti->first, ti->second));
  }

  cout << "combination_length,count,combination" << endl;
  while(!pq.empty()){
    count_idx x(pq.top());
    pq.pop();
    str item(x.item);
    cout << split(item).size() << "," << x.count << ",\"" << item << "\"" << std::endl;
  }

  return 0;
}
