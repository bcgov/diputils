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

/* co-occurence table for table of two variables plus identifier 20190120
 
This is a related script to co_occur.cpp, with some adjustments relating
to an analysis of education data */
#include<map>
#include<vector>
#include<string>
#include<sstream>
#include<fstream>
#include<iostream>
#include<algorithm>
#include"misc.h"
using namespace std;
std::map<std::string, long unsigned int> counts; // statistical co-occurence

void incr(std::string label){
  /* count string occurrences*/
  std::map<std::string, long unsigned int>::iterator ci;
  ci = counts.find(label);
  if(ci == counts.end()){
    //not yet counted
    counts[label] = 1;
  }
  else{
    // increase count
    counts[label] += 1;
  }
}

int main(int argc, char ** argv) {

  if(argc < 2) err("co_occur_educ [input csv name]");
  std::string filename(argv[1]);
  std::ifstream infile(filename);
  infile.seekg(0, infile.end);
  long unsigned int fsize = infile.tellg(); // filesize: for status indicator
  infile.seekg(0, infile.beg);
  std::string line; //buffer to hold a line of csv
  long int ci = 0;
  int percentage = 0; // for status indicator

  std::map<std::string, std::string> line_by_id; // aggregate lines
  std::map<std::string, std::string>::iterator mi; // pointer to an aggregated line

  while(std::getline(infile, line)){
    std::transform(line.begin(), line.end(), line.begin(), ::tolower); // to lower case
    std::vector<std::string> w(split(line, ','));

    if(ci == 0) if(w[w.size() -1] != "studyid") err("expected field studyid");

    string s_id(w[w.size() - 1]); // study id

    bool replace = true;
    mi = line_by_id.find(s_id);
    if(mi != line_by_id.end()){
      /* got a hit*/
      replace = false;
      if(w[0].substr(0,3) != std::string("non")){
        replace = true;
      }
    }
    // use most recent nonspecial needs flag
    if(replace) line_by_id[s_id] = line;

    if(ci < 10){
      // this should define a cout operator for vector<string>
      std::vector<std::string>::iterator it;
      int cd = 0;
      for(it = w.begin(); it !=w.end(); it++){
        if(cd > 0) cout << ",";
        cout << (*it) ;
        cd ++;
      }
      cout <<std::endl;
    }
    ci += 1;
    if(ci % 10000 ==0){
      int p = (int) (100. * (float)(infile.tellg()) / (float)(fsize));
      if(p > percentage ){
        percentage = p;
        cout << percentage << std::endl;
      }
    }
  }
  cout << "counting..." << std::endl;
  for(mi = line_by_id.begin(); mi != line_by_id.end(); mi++){
    string s_id(mi->first);
    string line(mi->second);
    std::vector<std::string> w(split(line, ','));
    incr(w[0]); //first field: behaviour code
    incr(w[1]); //second field: gender code
    incr(w[0] + std::string(",") + w[1]); //co-occurence code
  }

  /* output */
  for(std::map<std::string, unsigned long int>::iterator i=counts.begin(); i!=counts.end(); i++){
    std::cout << i->first <<"," << i->second << std::endl;
  }
  return 0;
}
