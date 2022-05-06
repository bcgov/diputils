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

#include"misc.h"
#include<ctime>
#include<string>
#include<fstream>
#include<iostream>
#include<algorithm>
using namespace std;

/* 20190307 filter edu data for cohort */

int main(int argc, char ** argv){
  if(argc < 2) err("usage: csv_filter_educ.cpp [data input.csv]\n");
  str dfn(argv[1]);
  str ofn(dfn + str("_filter_educ.csv"));
  str of2(dfn + str("_filter_educ_discard.csv"));
  cout << "data input file: " << dfn << endl;
  cout << "output file: " << ofn << endl;
  cout << "discard file: " << of2 << endl;

  ifstream infile(dfn);
  if(!infile.is_open()) err(str("failed to open file") + dfn);

  str line, label;
  register long unsigned int ci = 0;
  cout << "loading input file.." << endl;

  /* input file */
  mfile dfile(dfn, "rb");

  /* output files */
  ofstream outfile(ofn);
  if(!outfile.is_open()) err(str("failed to write-open file:") + ofn);

  /* this output file is for the stuff that's filtered out */
  ofstream outfil2(of2);
  if(!outfil2.is_open()) err(str("failed to write-open file:") + of2);

  /* read and write the csv header */
  dfile.getline(label);
  outfile << label;
  outfil2 << label;
  ci ++; // remember that we looked at the header already
  trim(label);
  if(label != "school_year,special_need_code_this_coll,age_group_jun_30,age_group_dec_31,is_sep_30_ref_enrol_flag,is_present_sep_30_flag,data_system_origin,grade_this_enrol,school_type_group_this_enrol,school_type_this_enrol,studyid") err("different fields expected");

  vector<str> fields(split(label));

  unsigned int i;
  unsigned int ul = label.size();
  vector<str> row;
  time_t t0; time(&t0);
  time_t t1;

  /* logic from 20190306:
  select studyID,
  case when Special_need_code_this_coll in ('NON SPECIAL NEED', 'P') then 'Non-Special Need'
  else 'Special Need'
  end as Special_Need_Flag
  from EDW_QUERY.CB_STULVLCB_FT_SCHLSTUD_VWD

  where --SCHOOL_YEAR BETWEEN '2000/2001' and '2017/2018'
  --and
  not GRADE_THIS_ENROL = 'HOME SCHOOLED STUDENT'
  and DATA_SYSTEM_ORIGIN in ('SLD', 'UNSPECIFIED')
  and AGE_GROUP_DEC_31 NOT in ('UNDER 5', 'UNKNOWN')
  and AGE_GROUP_JUN_30 NOT in ('UNDER 5', 'UNKNOWN')
  and SCHOOL_TYPE_GROUP_THIS_ENROL = 'BC SCHOOL'
  and SCHOOL_TYPE_THIS_ENROL = 'BC PUBLIC SCHOOL'
  and Is_Present_Sep_30_Flag = 'Present Sept 30'
  and Is_Sep_30_Ref_Enrol_Flag = 'Authority School'
  */

  set<str> req_fields; // required fields
  req_fields.insert(str("school_year"));
  req_fields.insert(str("grade_this_enrol"));
  req_fields.insert(str("data_system_origin"));
  req_fields.insert(str("age_group_dec_31"));
  req_fields.insert(str("age_group_jun_30"));
  req_fields.insert(str("school_type_group_this_enrol"));
  req_fields.insert(str("school_type_this_enrol"));
  req_fields.insert(str("is_present_sep_30_flag"));
  req_fields.insert(str("is_sep_30_ref_enrol_flag"));

  map<str, unsigned int> fi;
  set<str> avail_fields;
  vector<str>::iterator f;
  i = 0;
  for(f = fields.begin(); f != fields.end(); f++){
    lower(*f);
    avail_fields.insert(*f);
    fi[*f] = i ++;
  }

  map<str, unsigned int> col;
  set<str>::iterator g;
  for(g = req_fields.begin(); g != req_fields.end(); g++){
    if(avail_fields.count(*g) < 1){
      cout << "missing req'd field: " << *g << endl;
      err("missing required field");
    }
    col[*g] = fi[*g];
    cout << "col " << *g << " fi " << fi[*g] << endl;
  }

  cout << fields << endl;
  cout << "applying criteria.." << endl;

  str d;
  bool select = true;

  map<str, unsigned long int> count;
  while(dfile.getline(line)){

    // remember we need to add the non-ram loading, too, and hybrid loading..

    row = split(line);
    select = true;

    for(g = req_fields.begin(); g != req_fields.end(); g++){
      d = row[ fi[*g]]; // get the data associated with the required field
      lower(d); // convert to lower case

      if(((*g == "school_year") && (d < str("2000/2001") || d > str("2017/2018"))) ||
      ((*g == "grade_this_enrol") && (d == str("home schooled student"))) ||
      ((*g == "data_system_origin") && (!(d == "sld" || d == "unspecified"))) ||
      ((*g == "age_group_dec_31") && (d == "under 5" || d == "unknown")) ||
      ((*g == "age_group_jun_30") && (d == "under 5" || d == "unknown")) ||
      ((*g == "school_type_group_this_enrol") && (d != "bc school")) ||
      ((*g == "school_type_this_enrol") && (d != "bc public school")) ||
      ((*g == "is_present_sep_30_flag") && (d != "present sept 30")) ||
      ((*g == "is_sep_30_ref_enrol_flag") && (d != "authority school"))){

        if(count.count(*g) < 1){
          count[*g] = 0;
        }
        count[*g] += 1;
        select = false;
      }
    }

    if(select) outfile << "\n" << line;
    else outfil2 << "\n" << line;

    if((++ci) % 100000 == 0){
      // should put this into the file reader library
      size_t dfile_pos = dfile.tellg();
      size_t dfile_len = dfile.len();
      time(&t1);
      time_t dt = t1-t0;
      float mbps = (float)dfile_pos / ((float)dt * (float)1000000.);
      float eta = (float)dt * ((float)dfile_len - (float)dfile_pos) / ((float)dfile_pos);
      float p = 100. * (float)dfile_pos / (float) dfile_len;
      cout << "filt %" << p << " eta: " << eta << "s MB/s " << mbps << endl;
    }
  }
  outfile.close();
  outfil2.close();
  dfile.close();

  map<str, unsigned long int>::iterator mi;
  cout << "\n";
  for(mi = count.begin(); mi != count.end(); mi++){
    cout << mi->first << "," << mi->second << endl;
  }

  return 0;
}
