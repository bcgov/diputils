#include"misc.h"

/* split a string (a-la python) */
vector<string> split(string s, char delim){
  trim(s);
  bool extra = (s[s.size() - 1] == delim);
  std::vector<std::string> ret;
  std::istringstream iss(s);
  std::string token;
  while(getline(iss,token,delim)) ret.push_back(token);

  if(extra) ret.push_back(string(""));
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
  if(extra) ret.push_back(string(""));
  return ret;
}

void dbg(char c, int start_pos, int end_pos, string action, bool inside_quotes){
  cout << "c[" << c << "] start [" << start_pos << "] end [" << end_pos << "] ";
  cout << action << " " << (inside_quotes?string("inside"):string("outside")) << "]" <<endl;
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
          string add(s.substr(start_pos, end_pos - start_pos));
          trim(add, '\"');
          std::replace(add.begin(), add.end(), ',', ';');
          ret.push_back(add);
        }
        else{
          ret.push_back(string(""));
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
      string add(s.substr(start_pos, end_pos - start_pos + 1));
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
