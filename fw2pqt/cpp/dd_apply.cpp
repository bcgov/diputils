#include"misc.h"
#include<arrow/api.h>
#include<parquet/arrow/writer.h>
#include<parquet/exception.h>
#include<arrow/io/file.h>

using namespace std;
using arrow::StringBuilder;

arrow::Status main_fun(int argc, char ** argv){
  string ddf, dtf, ofn;
  if(argc < 3){
    err("usage: dd_apply.cpp [data dictionary.csv] [data input.dat]");
  }
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
      strip(*it);
      //std::transform(it->begin(), it->end(), it->begin(), ::tolower); // to lower case
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

  ci = 0;
  time_t t0;
  time(&t0);
  time_t t1;
  unsigned int i;
  vector<string> row;
  unsigned int n_f = label.size();

  arrow::MemoryPool* pool = arrow::default_memory_pool(); // init memory pool // try to delete this line?
  vector<std::shared_ptr<arrow::Field>> arrow_fields; // declare fields
  for0(ci, n_f) arrow_fields.push_back(arrow::field(label[ci], arrow::utf8()));
  std::shared_ptr<arrow::Schema> schema = arrow::schema(arrow_fields); // declare schema
  std::shared_ptr<arrow::Table> table; // declare a table: still need to initialize
  
  arrow::StringBuilder * string_builders = new arrow::StringBuilder[n_f]; // presumably using default memory pool

  ci = 0;
  string newline("\n");
  while(getline(infile2, d)){
    row.clear(); // clear row then add fields, subtract start[0] to handle start-index of 0 or 1
    for0(i, n_f) row.push_back(d.substr(start[i] - start[0], length[i]));
    for0(i, n_f) ARROW_RETURN_NOT_OK(string_builders[i].Append(d.substr(start[i] - start[0], length[i])));
    outfile << join(",", row) + newline;
  } 

  cout << "finalize arrays.." << endl;
  std::shared_ptr<arrow::Array> * arrays = (std::shared_ptr<arrow::Array> *)alloc(sizeof(std::shared_ptr<arrow::Array>) * n_f);
  for0(i, n_f) ARROW_RETURN_NOT_OK(string_builders[i].Finish(&arrays[i]));

  vector<std::shared_ptr<arrow::Array>> my_arrays;
  for0(i, n_f) my_arrays.push_back(arrays[i]);
 
  cout << "make table.." << endl; 
  table = arrow::Table::Make(schema, my_arrays);

  cout << "write parquet.." << endl;
  std::shared_ptr<arrow::io::FileOutputStream> out_file;
  PARQUET_ASSIGN_OR_THROW(out_file, arrow::io::FileOutputStream::Open("test.parquet"));
  PARQUET_THROW_NOT_OK(parquet::arrow::WriteTable(*table, arrow::default_memory_pool(), out_file, 3));

  // delete arrow_fields;
  return arrow::Status();
}

int main(int argc, char ** argv){
  main_fun(argc, argv);
}
