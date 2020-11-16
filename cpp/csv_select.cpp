/* 20190303 csv_select: filter a given CSV file for records where a given field matches the same field in the other file (somewhere)

use this for filtering a dataset for a specific cohort (represented by studyid in another file)

less vague example (python) from run_select_cohort.py:
import os
import sys
files = open("msp_files.txt").read().strip().split("\n")
for f in files:
cmd = "csv_select cohort.csv_studyid studyid " + f
print cmd
a = os.system(cmd)

20201016: note: in future, could select on matches of combinations of different fields?*/

#include"misc.h"
#include<cmath>
int main(int argc, char ** argv){
  if(argc < 4) err("usage: csv_select [file to filter by] [field name] [file to filter] .. [last file to filter]");

  string select_filename(argv[1]); // name of file to select by
  mfile f_s(select_filename, "rb"); // if this was too big to keep in mem, could use rewind() to re-scan it
  string s_f_name(argv[2]);
  unsigned int n_files = argc - 3;
  vector<string> file_names;

  cout << "number of files: " << n_files << endl;
  unsigned int i;
  for0(i, n_files){
    file_names.push_back(string(argv[i + 3]));
    FILE * f = fopen(argv[i + 3], "rb");
    if(!f) err("failed to open file");
    fclose(f);
  }
  cout << file_names << endl;

  string s;
  set<string> id; //set<const char *> id; //string> id;
  long unsigned int l_i = 0;
  unsigned int select_nf; // number of fields in the select file (probably don't use this)
  unsigned int s_f_i; // selected field index
  vector<string> words;

  while(f_s.getline(s)){
    trim(s);
    lower(s);
    words = split(s);

    if(l_i == 0){
      /* csv header */
      select_nf = words.size();
      int selected = false;
      for0(i, select_nf){
        if(words[i] == s_f_name){
          s_f_i = i;
          cout << "SELECTED_FIELD_INDEX (infile): " << s_f_i << endl;
          selected = true;
        }
      }
      if(!selected) err("failed to find selection field");
    }
    else{
      /* lower case, just in case */
      trim(words[s_f_i]);
      if(false && words[s_f_i].length() != 10){
        //should check if it's studyID we're using

        cout << "Error: " << words << endl;
        err("wrong number of digits in id");
      }

      id.insert(words[s_f_i]); //w_s_f_i); //words[s_f_i].c_str());
    }
    if((++ l_i) % 10000 == 0){
      f_s.status();
      cout << words << " " << words[s_f_i] << endl;
    }
  }
  f_s.close(); // free up the memory

  cout << "SELECTION SIZE " << id.size() << endl;

  unsigned int j;
  //w_s_f_i = NULL; // c string version of thing to match on

  //set<const char *> id_linked;
  unsigned long int n_matches = 0;
  for0(j, n_files){
    unsigned int nf = 0; // number of fields, this file
    cout << "Reading file: " << file_names[j] << endl;
    ifstream f_f;
    f_f.open(file_names[j]);
    if(!f_f.is_open()) err(str("failed to open input file: ") + file_names[j]);
    //mfile f_f(file_names[j], "rb");
    //cout << "\t[100%]\n";
    string ofn(file_names[j] + "_select-" + select_filename + ".csv");
    cout << " +w " << ofn << endl;

    FILE * outf = fopen(ofn.c_str(), "wb");
    if(!outf) err("failed to open output file");

    string of2(file_names[j] + "_select-" + select_filename + "-exclude-.csv");
    cout << " +w " << of2 << endl;

    FILE * out2 = fopen(of2.c_str(), "wb");
    if(!out2) err("failed to open output file");

    l_i = 0;
    bool matches_this_iter = false;
    size_t f_siz = fsize(file_names[j]);

    while(getline(f_f, s)){
      //f_f.getline(s))
      trim(s);
      lower(s);
      const char * s_c = s.c_str();
      words = split(s);
      if(l_i == 0){
        nf = words.size();
        int selected = false;
        /* make sure for this file, we can match the name of the appropriate field */
        for0(i, words.size()){
          trim(words[i]);
          vector<str> ws(split(words[i], '.'));
          if(ws.size() > 1){
            if(ws[ws.size() - 1] == s_f_name){
              s_f_i = i;
              selected = true;
            }
          }
          else{
            if(words[i] == s_f_name){
              s_f_i = i;
              cout << words << endl;
              cout << "SELECTED_FIELD_INDEX (outfile): " << s_f_i << endl;
              selected = true;
            }
          }
        }
        if(!selected) err("failed to find selected field"); // this should happen before we do the work.

        /* write the header */
        fwrite(s_c, strlen(s_c), 1, outf);
        fwrite(s_c, strlen(s_c), 1, out2); // 20190310 add support for "excluded" set
      }
      else{
        /* qc or data integrity checking. should have specific scripts to do this. */
        if(words.size() != nf){
          words = split_special(s);
          if(words.size() != nf){
            cout << words << endl;
            cout << "Unexpected number of fields (" << words.size() << ") at line number: " << l_i << " expected #: " << nf << endl;
            err("Remediation failed: wrong number of fields");
          }
        }
        trim(words[s_f_i]);
        if(false && words[s_f_i].length() != 10){
          cout << words << endl;
          cout << "line number: " << l_i << endl;
          err("wrong number of digits");
        }
        if(id.count(words[s_f_i]) > 0){
          fprintf(outf, "\n%s", s_c);
          matches_this_iter = true;
          n_matches ++;
        }
        else{
          fprintf(out2, "\n%s", s_c);
        }

      }
      if((++l_i) % 100000 ==0){
        size_t p = f_f.tellg();
        cout << "%" << 100. * float(p) / float(f_siz) << " match %" << ceil(100. * float(n_matches) / float(l_i -1)) << endl;
        matches_this_iter = false;
      }
    }
    f_f.close();
    fclose(outf);
    fclose(out2); // 20190310 added support for excluded / deselected set
  }

  cout << "size of filter id set:" << id.size() << endl;
  //cout << "size of filter id set that matched target set: " << id_linked.size() << endl;
  cout << "number of matches: " << n_matches << endl;
  set<const char *>::iterator it;

  return 0;
}