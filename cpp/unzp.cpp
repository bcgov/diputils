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
/* Unzip multiple zip files in parallel
 * oddly, python jumps out of the unix terminal. C++ does not!
 * This hook brings python back into the place where we can have nice things */
using namespace std;
int main(int argc, char** argv){
  if(argc > 1){
    system((str("gunzip ") + str(argv[1])).c_str());
  }
  else{
    system("ls -1 *.gz > ./.ls_1_gz.txt");
    ifstream f;
    f.open("./.ls_1_gz.txt");
    if(!f.is_open()){
      err("failed to open file: ./.ls_1_gz.txt");
    }

    ofstream o_f;
    o_f.open("./.unzp_jobs.txt");
    if(!o_f.is_open()) err("failed to open file: ./.unzp_jobs.txt");

    str s;
    while(getline(f, s)){
      trim(s);
      size_t f_siz = fsize(s);
      if(f_siz > 0){
        cout << "\tunzp " << s << endl;
        o_f << "unzp " << s << endl;

      }
    }
    f.close();
    o_f.close();

    // hypothetically 4 is enough unzip jobs to run at once!
    system("multicore ./.unzp_jobs.txt 4");
    system("rm -f ./.unzp_jobs.txt");
    system("rm -f ./.ls_1_gz.txt");
  }
  // 20190726 idea: do anything path-related in C environment:
  // this is where the paths follow the unix conventions?
  return 0;
}
