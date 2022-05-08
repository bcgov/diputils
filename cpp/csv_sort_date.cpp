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
/* low-memory date-sort: uses random file access 20190712

a csv line is represented efficiently in the following tuple:
(date yyyymmdd, location of record in file)

for each line, a tuple of that format is inserted in a priority_queue,
which sorts the above "tuple" objects based on the date

to output the sorted table, we visit the file location of the record,
and print out that line (record and line are synonyms) */

class date_idx{
  // date, file pointer tuple object
  public:
  str date;
  size_t idx;
  date_idx(str d = str(""), size_t i = 0){
    date = d;
    idx = i;
  }
  date_idx(const date_idx &a){
    date = a.date;
    idx = a.idx;
  }
};

bool operator<(const date_idx& a, const date_idx&b){
  return a.date > b.date; // priority_queue is max first, need to switch direction
}

int year, month, day;

inline void assert_date(str yyyy, str mm, str dd){
  // check date to make sure it's in the expected format
  year = atoi(yyyy.c_str());
  month = atoi(mm.c_str());
  day = atoi(dd.c_str());
  if(year < 1900 || year > 3000) err(str("unexpected data in year field: ") + yyyy);
  if(month < 1 || month > 12) err(str("unexpected data in month field: ") + mm);
  if(day < 1 || day > 31) err(str("unexpected data in day field: ") + dd);
  if(yyyy.size() != 4 || mm.size() != 2 || dd.size() != 2){
    cout << "yyyy " << yyyy << " mm " << mm << " dd " << dd << endl;
    err("please check date formatting");
  }
}

int main(int argc, char** argv){
  if(argc < 2) err("csv_sort_date [input file csv]\n");

  int j;
  str s("");
  size_t last_p;
  register int i;
  str fn(argv[1]);

  str ofn(fn + "_sorted.csv");

  ifstream f(fn);
  size_t f_size = fsize(fn);
  long unsigned int l_i = 0;
  if(!f.is_open())err("failed to open input file");

  ofstream of(ofn);
  if(!of.is_open()) err("failed to open output file");

  last_p = f.tellg();
  getline(f, s);
  of << s;
  //cout << last_p << " " << s << endl;
  l_i += 1;
  trim(s);
  lower(s);
  vector<str> w(split(s));
  // cout << "fields: " << w << endl;

  // date field detection
  set<char> punc; // punctuation characters to split on
  int n_f = w.size();
  for0(i, n_f){
    str x(w[i]);
    for0(j, x.size()){
      char c = x[j];
      if(isgraph(c) && (!isalnum(c))) punc.insert(c);
    }
  }

  int date_fi = -1; // selected date field indices
  set<int> date_fs; // possible date field indices
  for0(i, n_f){
    str x(w[i]);
    for(set<char>::iterator it = punc.begin(); it != punc.end(); it++){
      vector<str> wx(split(x, *it));
      for(vector<str>::iterator ti = wx.begin(); ti != wx.end(); ti++){
        if(*ti == "date"){
          date_fs.insert(i);
          date_fi = i;
        }
      }
    }
  }

  if(date_fs.size() > 1) err("failed to select a particular date field.\n\tadd more date logic");
  priority_queue<date_idx> dates;

  last_p = f.tellg();
  getline(f, s);
  trim(s);
  lower(s);
  w = split(s);
  str d(w[date_fi]);
  char d_delim = '\0';
  set<char> d_delims;
  for0(j, d.size()){
    if(isgraph(d[j]) && (!isalnum(d[j]))){
      d_delim = d[j];
      d_delims.insert(d[j]);
    }
  }
  if(d_delims.size() > 1){
    err("nonunique date delimiter: check integrity of date field");
  }
  w = split(d, d_delim);
  assert_date(w[0], w[1], w[2]); // check date formatting
  dates.push(date_idx(w[0] + w[1] + w[2], last_p));
  l_i += 1;

  last_p = f.tellg();
  while(getline(f, s)){
    trim(s);
    lower(s);
    w = split(s);
    if(w.size() != n_f){
      cout << "line number: " << l_i << endl;
      cout << "data: " << w << endl;
      err("unexpected number of fields");
    }

    d = w[date_fi];
    w = split(d, d_delim);
    assert_date(w[0], w[1], w[2]);

    dates.push(date_idx(w[0] + w[1] + w[2], last_p));

    l_i += 1; // might not need this
    last_p = f.tellg();
    if(l_i % 1000000 == 0){
      cout << "%" << 100. * float(last_p) / float(f_size) << endl;
    }
  }

  f.clear();
  date_idx d_idx;
  f.seekg(0, ios::beg);

  while(!dates.empty()){
    d_idx = dates.top();
    dates.pop();
    f.seekg(d_idx.idx);
    if(!getline(f, s)){
      cout << "file position (bytes): " << d_idx.idx << endl;
      err("failed getline");
    }
    //don't leave newline at very end
    of << endl << s;
  }
  f.close();
  return 0;
}