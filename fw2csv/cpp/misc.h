#ifndef _MISC_H_
#define _MISC_H_

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
#include<memory>
#include<sstream>
#include<fstream>
#include<iostream>
#include<limits.h>
#include<memory.h>
#include<algorithm>
#include<cctype>
#include<locale>
#include<ctime>

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

string cwd();

/* split a string (a-la python) */
vector<string> split(string s, char delim);
vector<string> split(string s); // comma
vector<string> split_special(string s); // comma with possible commas inside quotation marks!
string join(const char * delim, vector<string> s);

template<class T> std::ostream& operator << (std::ostream& os, const std::vector<T>& v){
  os << "[";
  for (typename std::vector<T>::const_iterator ii = v.begin(); ii != v.end(); ++ii){
    if(ii != v.begin()) os << ", ";
    os << "'" << *ii << "'";
  }
  os << "]";
  return os;
}

template<class T> std::ostream& operator << (std::ostream& os, const std::set<T>& v){
  os << "{";
  for (typename std::set<T>::const_iterator ii = v.begin(); ii != v.end(); ++ii){
    if(ii != v.begin()) os << ", ";
    os << *ii;
  }
  os << "}";
  return os;
}

template<class A, class B> std::ostream& operator << (std::ostream& os, const std::map<A, B>& v){
  os << "{" << endl;
  for (typename std::map<A, B>::const_iterator ii = v.begin(); ii != v.end(); ++ii){
    if(ii != v.begin()) os << ", ";
    os << ii->first << ":" << ii->second;
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


//a trim from start (in place)
static inline std::string ltrim(std::string s){
  int i = 0;
  for(int j = 0; j < s.length(); j++){
    if(!std::isspace(s[j])) break;
    else i ++;

  } 
  std::string r(s.substr(i, s.length() - i));
  return r;
}

// trim from end (in place)
static inline std::string rtrim(std::string s){
  int i = 0;
  for(int j = s.length() - 1; j >= 0; j--){
    if(std::isspace(s[j])) i ++;
    else break;
  }
  std::string r(s.substr(0, s.length() - i));
  return r;
}

// trim from both ends (in place)
static inline std::string trim(std::string s){
  return rtrim(ltrim(s));
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
  string ret("");
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


#endif
