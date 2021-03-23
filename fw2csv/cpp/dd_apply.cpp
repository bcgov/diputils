#include"misc.h"
using namespace std;

int main(int argc, char ** argv){
  string ddf, dtf, ofn;

  if(argc < 3) err("usage: dd_apply.cpp [data dictionary.csv] [data input.dat]");
  else{
    ddf = string(argv[1]);
    dtf = string(argv[2]);
  }
  ofn = string(dtf + string("_dd_apply.csv"));
  cout << "data dictionary file: " << ddf << endl;
  cout << "data input file: " << dtf << endl;
  cout << "output file: " << ofn << endl;

  ifstream infile(ddf);
  if(!infile.is_open()) err(string("failed to open file") + ddf);

  string d;
  size_t ci = 0;
  vector<string> label;
  vector<string>::iterator it;
  vector<int> start, stop, length;

  while(getline(infile, d)){
    ci++; // process input line by line
    vector<string> w(split(d, ','));
    for(it = w.begin(); it != w.end(); it++){
      *it = strip(*it);
    }
    if(ci==1){
      if(w[0] != string("start")) err(string("expected field 0 ") + w[0]);
      if(w[1] != string("stop")) err(string("expected field 1 ") + w[1]);
      if(w[2] != string("length")) err(string("expected field 2 ") + w[2]);
      if(w[3] != string("label") && w[3] != string("name abbrev")) err(string("expected field 3 ") + w[3]);
    }
    else{
      start.push_back(atoi(w[0].c_str()));
      stop.push_back(atoi(w[1].c_str()));
      length.push_back(atoi(w[2].c_str()));
      label.push_back(w[3]);
      if(atoi(w[1].c_str()) + 1 - atoi(w[0].c_str()) != atoi(w[2].c_str())) err("length mismatch error");
    }
  }

  cout << "start: " << start << endl;
  cout << "stop: " << stop << endl;
  cout << "length: " << length << endl;
  cout << "label: " << label << endl;

  ifstream infile2(dtf);
  if(!infile2.is_open()) err(string("failed to open file") + dtf);

  ofstream outfile(ofn);
  if(!outfile.is_open()) err(string("failed to write-open file:") + ofn);

  if(label.back() == string("LINEFEED")) label.pop_back(); // linefeed shouldn't be a thing
  outfile << join(",", label) << "\n"; // write header row to outfile

  unsigned int i;
  vector<string> row;
  unsigned int n_f = label.size();

  ci = 0;
  string newline("\n");
  while(getline(infile2, d)){
    row.clear(); // clear row then add fields, subtract start[0] to handle start-index of 0 or 1
    for0(i, n_f) row.push_back(d.substr(start[i] - start[0], length[i]));
    for0(i, n_f) row[i] = trim(row[i]);
    if(ci++ > 0) outfile << newline;
    outfile << join(",", row);
  }

  return 0;
}