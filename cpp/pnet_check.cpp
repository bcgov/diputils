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

/* 20190711 pnet_check.cpp: check pharmanet (clm*, dsp*) files for:
1) reversals: dspd_qty (quantity dispensed) and dspd_days_sply (days supplied) should not be negative
2) reversals: claim status (pcare_pmt_sts_label) in clm_rpt should contain "P" and "U" but not "R"
3) vet billing: practitioner identification number (prscr_prac_lic_body_idnt) shouldn't contain the code "V */
#include"misc.h"

// print debug info and crash
void debug(ofstream &g, str s, str fn, long int li, vector<str> w, const char * msg){
  cout << str(msg) << "," << fn << "," << s << endl;
  g << str(msg) << "," << fn << "," << s << endl;
  //"file: " << fn << endl << "line: " << li << endl << w << endl;
  // err(msg);
}

int main(int argc, char ** argv){
  if(argc < 2) err("pnet_check [input file 1] .. [input file n]\n\tCheck pharmanet csv files (clm*, dsp*) for reversals or veterinary billing\n");

  str s;
  int i, j;
  long int li = 0;
  size_t cur_pos = 0;
  size_t total_size = 0;
  int n_files = argc - 1;

  // field position idx
  int dspd_qty = -1;
  int dspd_days_sply = -1;
  int pcare_pmt_sts_label = -1;
  int prscr_prac_lic_body_idnt = -1;

  // more field position idx
  int srv_date = -1;

  // check we can open all the files
  for0(i, n_files){
    ifstream f(argv[i + 1], ios::binary);
    if(!f.is_open()) err("failed to open input file\n");
    f.close();
    total_size += fsize(str(argv[i + 1]));
  }

  // do the work
  for0(i, n_files){
    map<str, long unsigned int> reversal_count;
    map<str, long unsigned int> veterinary_count;
    map<str, long unsigned int> total_count;

    // open file
    str fn(argv[i + 1]);
    ifstream f(fn, ios::binary);
    cout << fn << endl;
    getline(f, s);
    li = 1;

    ofstream cf(fn + str("_clean"));
    if(!cf.is_open()) err("failed to open output file");

    cf << s; // write header to output

    ofstream g(fn + str("_bad-data"));
    if(!g.is_open()) err("failed to open output file");
    trim(s);
    g << "errtype,datafile," << s << endl;

    // read the field names and remove "front prefix" e.g. pc. or de.
    str fields(s);
    vector<str> w(split(s));
    for0(j, w.size()){
      trim(w[j]);
      lower(w[j]);
      vector<str> w2(split(w[j], '.')); // matches field modulo prefix
      if(w2.size() > 1){
        w[j] = w2[1];
      }
      trim(w[j], '*');

      // index of desired fields
      if(w[j] == str("dspd_qty")) dspd_qty = j;
      if(w[j] == str("dspd_days_sply")) dspd_days_sply = j;
      if(w[j] == str("pcare_pmt_sts_label")) pcare_pmt_sts_label = j;
      if(w[j] == str("prscr_prac_lic_body_idnt")) prscr_prac_lic_body_idnt = j;

      if(w[j] == str("srv_date")) srv_date = j;
    }
    cout << "idx[dspd_qty]" << dspd_qty << endl;
    cout << "idx[dspd_days_sply]" << dspd_days_sply << endl;
    cout << "idx[pcare_pmt_sts_label]" << pcare_pmt_sts_label << endl;
    cout << "idx[prscr_prac_lic_body_idnt]" << prscr_prac_lic_body_idnt << endl;

    str r("r");
    str v("v");

    // for every data record
    while(getline(f, s)){
      bool clean = true;
      w = split(s);

      if(pcare_pmt_sts_label >=0){
        lower(w[pcare_pmt_sts_label]);
        trim(w[pcare_pmt_sts_label]);
      }

      if(prscr_prac_lic_body_idnt >=0){
        trim(w[prscr_prac_lic_body_idnt]);
        lower(w[prscr_prac_lic_body_idnt]);
      }

      // check date format
      vector<str> yyyy_mm_dd(split(w[srv_date], '-'));
      if(yyyy_mm_dd.size() != 3) err("unexpected date format");
      str yyyy(yyyy_mm_dd[0]);

      // check for reversals
      if((dspd_qty >= 0 && atoi(w[dspd_qty].c_str()) < 0) || // have the field, and it's value is negative..
      (dspd_days_sply >=0 && atoi(w[dspd_days_sply].c_str()) < 0) ||
      (pcare_pmt_sts_label >=0 && w[pcare_pmt_sts_label] == r)){
        if(reversal_count.count(yyyy) == 0){
          reversal_count[yyyy] = 0;
        }
        reversal_count[yyyy] += 1;
        debug(g, s, fn, li, w, "reversal");
        clean = false;
      }

      // check for veterinary data
      if(prscr_prac_lic_body_idnt >=0){
        trim(w[prscr_prac_lic_body_idnt]);
        lower(w[prscr_prac_lic_body_idnt]);
        if(w[prscr_prac_lic_body_idnt] == v){
          if(veterinary_count.count(yyyy) == 0){
            veterinary_count[yyyy] = 0;
          }
          veterinary_count[yyyy] += 1;
          debug(g, s, fn, li, w, "veterinary");
          clean = false;
        }
      }

      // count all records by year
      if(total_count.count(yyyy) == 0){
        total_count[yyyy] = 0;
      }
      total_count[yyyy] += 1;

      if(clean){
        cf << endl << s;
      }

      if(li % 100000 == 0){
        float percent = 100. * float(cur_pos + f.tellg()) / float(total_size);
        cout << "%" << percent << endl;
        FILE * pf = fopen((fn + str("_status")).c_str(), "ab");
        if(!pf) err("failed to open status file");
        else{
          fprintf(pf, "%f\n", percent);
          fclose(pf);
        }
      }
      li += 1;
    }
    //getline
    f.close();
    g.close();
    cf.close();

    FILE * pf = fopen((fn + str("_status")).c_str(), "ab");
    if(!pf) err("failed to open status file");
    else{
      fprintf(pf, "reversal_count = {");
      for(map<str, long unsigned int>::iterator it = reversal_count.begin(); it != reversal_count.end(); it++){
        if(it != reversal_count.begin()) fprintf(pf, ",");
        fprintf(pf, "\"%s\":%ld", (it->first).c_str(), it->second);
      }
      fprintf(pf, "}\n");

      fprintf(pf, "veterinary_count = {");
      for(map<str, long unsigned int>::iterator it = veterinary_count.begin(); it != veterinary_count.end(); it++){
        if(it != veterinary_count.begin()) fprintf(pf, ",");
        fprintf(pf, "\"%s\":%ld", (it->first).c_str(), it->second);
      }
      fprintf(pf, "}\n");

      fprintf(pf, "total_count = {");
      for(map<str, long unsigned int>::iterator it = total_count.begin(); it != total_count.end(); it++){
        if(it != total_count.begin()) fprintf(pf, ",");
        fprintf(pf, "\"%s\":%ld", (it->first).c_str(), it->second);
      }
      fprintf(pf, "}\n");
      // fprintf(pf, "reversal count, %ld, veterinary count, %ld\n", reversal_count, veterinary_count);
      fclose(pf);
    }
    cur_pos += fsize(fn);
  }
  return 0;
}
