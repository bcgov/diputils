//  Copyright 2019 Province of British Columbia
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

#include"misc.h"
string cwd(){
  char s[PATH_MAX];
  char * result = _cwd(s, PATH_MAX);
  return string(s);
}

/* split a string (a-la python) */
vector<string> split(string s, char delim){
  trim(s);
  bool extra = (s[s.size() - 1] == delim);
  std::vector<std::string> ret;
  std::istringstream iss(s);
  std::string token;
  while(getline(iss,token,delim)) ret.push_back(token);

  if(extra) ret.push_back(str(""));
  return ret;
}

/* split a string (a-la python) */
vector<string> split(string s){
  trim(s);
  const char delim = ',';
  bool extra = (s[s.size() -1] == delim);

  std::vector<std::string> ret;
  std::istringstream iss(s);
  string token;
  while(getline(iss,token,delim)) ret.push_back(token);

  vector<string>::iterator it;
  for(it = ret.begin(); it != ret.end(); it++){
    trim(*it);
  }
  if(extra) ret.push_back(str(""));
  return ret;
}

void dbg(char c, int start_pos, int end_pos, str action, bool inside_quotes){
  cout << "c[" << c << "] start [" << start_pos << "] end [" << end_pos << "] " << action << " " << (inside_quotes?str("inside"):str("outside")) << "]" <<endl;
}

/*
#include"misc.cpp"
int main(int argc, char ** argv){
  str data("1,\",,2,3\",,,hello,12345,\"{12,12,12}\",word");
  cout << "[" << data << "]" << endl;
  cout << split(data) << endl;
  vector<str> ss(split_special(data));
  cout << "good:"<< ss << endl;
  cout << "bad:" << split(data) << endl;
  cout << data << endl;
  return 0;
}
*/

vector<string> split_special(string s){
  // split string function for csv files that may have commas inside of double quotation marks!
  vector<string> ret;
  if(s.size() == 0) return ret;
  int start_pos = 0;
  int end_pos = 0; // left-inclusive indices of selection (right index is not inclusive)
  bool inside_quotes = false;
  char c = s[end_pos];
  while(end_pos < s.size() - 1){
    while(c != ',' && c != '\"' && end_pos < s.size() -1){
      c = s[++end_pos];
    }
    // hit a comma, a double-quotes mark, or got to the end
    if(c == ','){
      if(!inside_quotes){
        if(end_pos > start_pos){
          str add(s.substr(start_pos, end_pos - start_pos));
          trim(add, '\"');
          std::replace(add.begin(), add.end(), ',', ';');
          ret.push_back(add);
        }
        else{
          ret.push_back(str(""));
        }
        start_pos = ++end_pos;
        c = s[end_pos];
      }
      else{
        c = s[++end_pos];
      }
    }
    else if(c == '\"'){
      inside_quotes = inside_quotes?false:true;
      c = s[++end_pos];
    }
    else{
      // out of bounds
      str add(s.substr(start_pos, end_pos - start_pos + 1));
      trim(add, '\"');
      std::replace(add.begin(), add.end(), ',', ';');
      ret.push_back(add);
      return ret;
    }
  }
  return ret;
}

/*
e.g.:
str join_(vector<str> d){
  const char * d = "_\0";
  return join(d, ans);
}
*/
string join(const char * delim, vector<string> s){
  string ret("");
  string d(delim);
  for(vector<string>::iterator it = s.begin(); it!=s.end(); it++){
    if(it!=s.begin()) ret += d;
    ret += *it;
  }
  return ret;
}

void err(string msg){
  cout << "Error: " << msg << endl;
  exit(1);
}

void err(const char * msg){
  err(string(msg));
}

void * balloc(long unsigned int nb){
  void * d = malloc(nb);
  memset(d, '\0', nb);
  return (void *)d;
}

FILE * wopen(string fn){
  FILE * f = fopen(fn.c_str(), "wb");
  if(!f) err("failed to open file for writing");
  return f;
}

mfile::mfile(string f_n, char * mode){
  /*
  need a flag for if we don't open the whole thing in ram..
  */
  if(mode[0] !='r') err("write mode not yet supported");
  if(mode[1] != 'b') err("incorrect mode str: rb, wb");
  if(mode[0] != 'r' && mode[0] != 'b') err("incorrect mode str: rb, wb");
  fp = fopen(f_n.c_str(), mode);
  if(!fp) err("failed to open file");
  fs = size(fp);
  d = (char *)alloc(fs);
  size_t nr = fread(d, fs, 1, fp);
  if(nr != 1) err("failed to read file");
  c_pos = l_pos = 0;
  last_pos = 0;
  start_t = clock();
}

int mfile::getline(string & buf){
  c_pos = l_pos;
  for(c_pos == l_pos; c_pos < fs; c_pos++){
    c = d[c_pos]; // printf("\nc '%c'\n", c);
    if(c == '\n' || c == '\r') break;
  }
  if(c_pos == l_pos) return false;
  memcpy(&s_bf[0], &d[l_pos], c_pos - l_pos);
  s_bf[c_pos - l_pos] = '\0'; // null termintor
  buf = s_bf;
  while(c= d[c_pos] == '\n' || c == '\r') c_pos ++;
  l_pos = c_pos;
  return true;
}

void mfile::rewind(){
  c_pos = l_pos = 0;
}

void mfile::close(){
  fclose(fp);
  free(d);
}

void mfile::status(){
  cout << "%" << 100.* ((float)l_pos / (float)fs); // << " MB/s " ;
  clock_t t = clock();
  if(last_pos > 0){
    clock_t duration = t - last_t;
    size_t d_pos = l_pos - last_pos;
    double dt = (double) duration / (double) CLOCKS_PER_SEC;
    cout << " MB/s: " << ((float)d_pos / (float)1000000.) / (float)dt << " ";
  }
  last_pos = l_pos;
  last_t = t;
}

size_t mfile::tellg(){
  return c_pos;
}
size_t mfile::len(){
  return fs;
}

/* get size of file pointer */
size_t size(FILE * f){
  fseek(f, 0L, SEEK_END);
  size_t sz = ftell(f);
  rewind(f);
  return sz;
}

size_t fsize(string fn){
  FILE * f = fopen(fn.c_str(), "rb");
  if(!f) return (size_t) 0;
  size_t fs = size(f);
  fclose(f);
  return fs;
}

bool exists(string fn){
  return fsize(fn) > 0;
}

void rewind(ifstream &a){
  a.clear();
  a.seekg(0);
}

// priority_queue max-first, we want min
bool operator < (const f_i &a, const f_i &b){
  return a.f > b.f;
}

/*
bool operator < (const f_ij &a, const f_ij &b){
  return a.f > b.f;
}
*/
