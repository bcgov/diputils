/* 20190531 unique.cpp: filter for unique values of A) or B):

A) the record as a whole (default) 
  ```unique input_data_file.csv```

This is the primary intended usage as tabular datasets often contain duplicated records. In this case de-duplication is necessary to ensure analytic measurements are as accurate as possible

B) filtering for unique values of specific columns:
  ```unique input_data_file.csv studyid```

Would produce an output table with one row per unique studyid (in that example you would only do this is you wanted to select just one row, for each service user)
    
Note: This version of the program is  case sensitive.*/
#include"misc.h"
using namespace std;

int main(int argc, char ** argv){
  if(argc < 2) err("usage:\n\tunique.cpp [input file] [field 1] ... [field n]\n\tdefault: all fields");
  int n_fields = argc - 2; // number of fields to filter on

  string dfn(argv[1]); // input file to filter
  ifstream dfile(dfn);
  if(!dfile.is_open()) err(string("failed to open input data file:") + dfn);
  size_t total_size = fsize(dfn);

  // cols to filter on
  unordered_set<str> d;
  for(int i = 0; i < n_fields; i++){
    string f(argv[i + 2]);
    // lower(f);
    trim(f);
    cout <<"\tfilter on col: " << f << endl;
    d.insert(f);
  }

  // output file: include filtered field names in the name of the output file (for sanity)
  string ofn(dfn + string("_unique-"));
  for(unordered_set<str>::iterator it = d.begin(); it!=d.end(); it++){
    ofn += *it + string("-");
  }
  ofn = ofn + string("_") + string(".csv");
  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);

  cout << "data input file: " << dfn << endl;
  cout << "data output file: " << ofn << endl;

  string line;
  size_t last_p = 0;
  vector<string> row;
  long unsigned int ci = 0;
  unordered_map<string, string> unique;

  // get the field names
  getline(dfile, line);
  trim(line);
  // lower(line);
  row = split(line, ',');

  set<int> indices;
  for(int k=0; k<row.size(); k++){
    string s(row[k]);
    trim(s);
    if(d.count(s) > 0){
      indices.insert(k);
    }
  }
  outfile << line << endl;

  int ii;
  unordered_set<int>::iterator it;
  // in the future we should reimplement getline to read whole file into ram if can, or use ramless, different interleaves or latencies
  while(getline(dfile, line)){
    trim(line);
    if(n_fields == 0){
      // lower(line);
      if(unique.count(line) < 1){
        unique[line] = line;
      }
    }
    else{
      row = split(line, ',');
      str idx("");

      ii = 0;
      for(it = indices.begin(); it != indices.end(); it++){
        if(ii == 0){
          idx += str(",");
        }
        idx += (row[*it]);
        ii += 1;
      }
      trim(idx);
      //lower(idx);
      if(unique.count(idx) < 1){
        unique[idx] = line;
      }
    }
    if(ci % 100000 == 0){
      size_t p = dfile.tellg();
      cout << "%" << 100. * float(p) / float(total_size);
      cout << endl;
      last_p = p;
    }
    ci ++;
  }
  dfile.close();

  cout << "outputting last unique lines: " << unique.size() << " of " << ci << endl;
  ci = 0;
  for(unordered_map<string, string>::iterator it = unique.begin(); it != unique.end(); it++){
    outfile << it->second << endl;
    if(++ci % 100000 == 0){
      cout << "%" << 100. * float(ci) / float(unique.size()) << endl;
    }
  }
  outfile.close();
  return 0;
}
