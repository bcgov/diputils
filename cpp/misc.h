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

#ifndef _MISC_H_
#define _MISC_H_
//---------------------------------------------------------------------------//
// misc.h: helper functions //
// date: 20190124 //
//---------------------------------------------------------------------------//

/* shorthand for for loops from 0 to N */
#define for0(i,n) for(i = 0; i < n; i++)

#define STR_MAX 16384

#define mtx_lock pthread_mutex_lock
#define mtx_unlock pthread_mutex_unlock

#include<map>
#include<set>
#include<queue>
#include<vector>
#include<string>
#include<sstream>
#include<fstream>
#include<iostream>
#include<limits.h>
#include<memory.h>
#include<algorithm>
#include"ansicolor.h"
#include<unordered_set>
#imclude<unordered_map>

using namespace std;

#include <stdio.h> /* defines FILENAME_MAX */
#ifdef WINDOWS
#include <direct.h>
#define _cwd _getcwd
#else
#include <unistd.h>
#define _cwd getcwd
#endif

void rewind(ifstream &a);

#define str string
string cwd();

/* split a string (a-la python) */
vector<string> split(string s, char delim);
vector<string> split(string s); // comma
vector<string> split_special(string s); // comma with possible commas inside quotation marks!
string join(const char * delim, vector<string> s);

template<class T> std::ostream& operator << (std::ostream& os, const std::vector<T>& v){
  os << "[";
  for (typename std::vector<T>::const_iterator ii = v.begin(); ii != v.end(); ++ii){
    os << " '" << *ii << "'";
  }
  os << "]";
  return os;
}

template<class T> std::ostream& operator << (std::ostream& os, const std::set<T>& v){
  os << "{";
  for (typename std::set<T>::const_iterator ii = v.begin(); ii != v.end(); ++ii){
    os << " " << *ii;
  }
  os << "}";
  return os;
}

template<class A, class B> std::ostream& operator << (std::ostream& os, const std::map<A, B>& v){
  os << "{" << endl;
  for (typename std::map<A, B>::const_iterator ii = v.begin(); ii != v.end(); ++ii){
    os << ii->first << ":" << ii->second << ","; //endl;
  }
  os << "}" << endl;
  return os;
}

void err(string msg);

void err(const char * msg);

void * balloc(long unsigned int nb);

/* allocate memory */
inline void * alloc(size_t nb){
  void * d = malloc(nb);
  if(!d){
    printf("%zu\n", nb);
    err("failed to allocate memory");
  }
  memset(d, '\0', nb);
  return d;
}

#include <algorithm>
#include <cctype>
#include <locale>

//a trim from start (in place)
static inline void ltrim(std::string &s){
  s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](int ch){
    return !std::isspace(ch);
  }
  ));
}

// trim from end (in place)
static inline void rtrim(std::string &s){
  s.erase(std::find_if(s.rbegin(), s.rend(), [](int ch){
    return !std::isspace(ch);
  }
  ).base(), s.end());
}

// trim from both ends (in place)
static inline void trim(std::string &s){
  ltrim(s);
  rtrim(s);
}

// trim from start (copying): not implemented properly
static inline std::string ltrim_copy(std::string s){
  ltrim(s);
  return s;
}

// trim from end (copying): not implemented properly
static inline std::string rtrim_copy(std::string s){
  rtrim(s);
  return s;
}

// trim from both ends (copying): not implemented properly
static inline std::string trim_copy(std::string s){
  trim(s);
  return s;
}

static inline void trim(std::string &s, char delim){
  str ret("");
  int end = s.size() - 1;
  int start = 0;
  while(s[start] == delim) start += 1;
  while(s[end] == delim) end -= 1;
  s = s.substr(start, 1 + end - start);
}

#define strip trim

/* convert to lower case */
static inline void lower(std::string & s){
  std::transform(s.begin(), s.end(), s.begin(), ::tolower);
}

static inline std::string lower_copy(std::string &s){
  string r(s);
  std::transform(r.begin(), r.end(), r.begin(), ::tolower);
  return r;
}

/* get size of file pointer */
size_t size(FILE * f);
size_t fsize(string fn);

bool exists(string fn);

// in-memory reader (writer to be implemented)
// note this should be able to modulate between available protocols (like ifstream,
// ofstream, etc. , fwrite, fread, if available)

FILE * wopen(string fn);

class mfile{
  FILE * fp;
  char * d;
  size_t fs;
  char s_bf[STR_MAX];
  char c;

  size_t l_pos; // position of start of current line
  size_t c_pos; // present read position within line

  //T x; // just using this to trick the compiler to let us implement the class in the header!
  public:

  mfile(string f_n, char * mode);
  int getline(string & buf);
  void rewind();
  void close();

  clock_t start_t, last_t;
  size_t last_pos;
  size_t tellg();
  size_t len();
  void status();

  };

  /* function to produce a distributed map of finite trajectory generation, with information-theoretically optimal compression */
  // this requires "class SA" (list / map hybrid)
  //
  // use this to algebraically encode e.g. lists of filenames in the format: msp2000-17, for continuous times..
  // e.g, [ab, ac] --> a[b,c]
  // [abc, ac] --> a[b[c],c]
  //
  //
  //

// float-int tuple for sorting distances
class f_i{
  public:
  float f;
  size_t i;
  f_i(float g = 0., size_t h = 0){
    // constructor. 0-index is null
    f = g;
    i = h;
  }
  f_i(const f_i &a){
    // copy constructor
    f = a.f;
    i = a.i;
  }
};

bool operator < (const f_i &a, const f_i &b);

/*

// float-int tuple for sorting distances
class f_ij{
  public:
  float f;
  size_t i,j;
  f_ij(float f_ =0, size_t i_=0, size_t j_=0){
    // constructor. 0-index is null
    f = f_;
    i = i_;
    j = j_;
    cout << " fij(" << f << "," << i << "," << j << ")" << endl;
  }
  f_ij(const f_ij &a){
    // copy constructor
    f = a.f;
    i = a.i;
    j = a.j;
   cout << "*fij(" << f << "," << i << "," << j << ")" << endl;
  }
};

bool operator < (const f_ij &a, const f_ij &b);
*/
#endif
