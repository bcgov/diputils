/*
 * Select records with indicated field(s) blank
 */
#include"misc.h"
int main(int argc, char ** argv){
  if(argc < 3){
    err("csv_select_blank.cpp [csv file name] [field to select blanks on] # select records with indicated field, blank");
  }
  // check input file exists
  str inf(argv[1]);
  cout << "input file: " << inf << endl;
  if(!exists(inf)){
	  err("failed to open input file");
 }

  // open input file
  ifstream f(inf);
  if(!f.is_open()) err("failed to open input file");
  
  // print output file info
  str of1(inf + str("_blank.csv"));
  str of2(inf + str("_unblank.csv"));
  cout << "selected file: " << of1 << endl;
  cout << "deselected file: " << of2 << endl;

  // open output files
  ofstream f1(of1);
  ofstream f2(of2);
  if(!f1.is_open()) err("failed to open selected file.");
  if(!f2.is_open()) err("failed to open deselected file.");

  // get selected field index
  int i;
  str s, hdr;
  int f_i = -1;
  getline(f, hdr);
  vector<str> fields(split(hdr));
  for0(i, fields.size()){
    if(fields[i] == str(argv[2])){
      f_i = i;
    }
  }
  cout << "selected field: " << fields[f_i] << endl;

  // write headers
  f1 << hdr;
  f2 << hdr;

  vector<str> c;
  while(getline(f, s)){
      c = split(s);
      str t(c[f_i]);
      strip(t);
      if(t == str("")){
	      f1 << endl << s;
      }
      else{
	      f2 << endl << s;
      }

  }
  f1.close();
  f2.close();
  f.close();
  return 0;
}

