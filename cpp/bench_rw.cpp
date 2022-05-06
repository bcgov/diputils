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
#include<time.h>
#include<stdio.h>
#include<stdlib.h>
using namespace std;
/* Test memory write speed!  */
int main(int argc, char ** argv){
  if(argc < 1){
    err("bench_rw.cpp [test file path]");
  }

  str fn(argv[1]);
  if(exists(fn)){
    err(str("test file already exists: ") + fn);
  }
  FILE * f = fopen(fn.c_str(), "wb");
  size_t g = 1024 * 1024 * 1024;
  size_t bytes = 1 * g;
  char * d = (char *)alloc(g);
  if(!d) err("failed to allocate memory");
  else printf("allocated memory.\n");

  int i;
  size_t gb = bytes / (1024 * 1024 * 1024);

  // looping as couldn't seem to allocate more than 1GB at once
  clock_t t0 = clock();
  for0(i, gb){
    size_t wb = fwrite(d, g, 1, f);
  }
  clock_t t1 = clock();

  float t = (float)(t1 - t0) / ((float)CLOCKS_PER_SEC);
  printf("data written: %ld (bytes)\n", (long int)bytes);
  printf("time to write: %f (s)\n", t);
  printf("MB per second: %f\n", ((float)bytes) / (t * (float)(1024 * 1024)));
  fclose(f);
  free(d);
}
