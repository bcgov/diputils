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
/* distance matrix calulation for tabular dataset, for use in clustering algorithm (s)*/
#include"misc.h"
#include<cmath>
#include<pthread.h>

size_t skip_factor;
str hdr; // csv header, first line of csv file
vector<str> csv; // csv input data lines
str * dat;

size_t n_row, n_col, n_str;

void read_data(str fn){
  size_t ci = 0; // row count

  // open the input data
  ifstream g(fn);
  if(!g.is_open()) err("failed to opend input file");
  string s;

  // read header
  getline(g, hdr);
  while(getline(g, s)){
    csv.push_back(s);
    ci ++;
  }
  g.close();
  cout << "fields: " << split(hdr);
  cout << "rcords: " << csv.size() << endl; // first record is header
  // n.b. need to project that onto the data
}

pthread_mutex_t print_mtx;
void cprint(str s){
  mtx_lock(&print_mtx);
  cout << s << endl;
  mtx_unlock(&print_mtx);
}

size_t k_max, k_use, nxt_j;
pthread_mutex_t nxt_j_mtx;
pthread_attr_t attr; // specify threads joinable

// arrays that will get written to disk
float * dmat_d;
size_t * dmat_i;

void * dmat_threadfun(void * arg){
  float d;
  str x, y;
  str us("unknown");
  size_t i, k, u, my_nxt_j;
  k = (size_t) arg;
  cprint(str("worker (") + to_string(k) + str(")"));
  priority_queue<f_i> pq;

  while(1){
    mtx_lock(&nxt_j_mtx);
    my_nxt_j = nxt_j++;
    mtx_unlock(&nxt_j_mtx);

    if(my_nxt_j > n_row -1){
      cprint(str(" exit worker(" + to_string(k) + str(")")));
      return NULL;
    }
    // got a job
    cprint(str("*") + to_string(k) + str(" pickup ") + to_string(my_nxt_j));

    // only calculate upper matrix
    for0(i, n_row){
      // don't calculate distance of a point with itself
      if(i != my_nxt_j){

        d = 0.;
        for0(u, n_col){
          x = dat[my_nxt_j * n_col + u];
          y = dat[i * n_col + u];

          if(x == y && (x != us && y != us)){
            // d += 1;
            //cout << (str(" sme: ") + x + str(",") + y) << endl;
          }
          else{
            d += 1.;
            //cout << (str(" dif: ") + x + str(",") + y) << endl;
          }
        }
        // cout << "d " << d << " i " << i << endl;
        pq.push(f_i(d, i));
        // cprint(str("i ") + to_string(my_nxt_j) + str(" j ") + to_string(i) + str(" d ") + to_string(d));
        //dmat[my_next_j * n_records + i] = d;
      }
    }

    /*
    if(pq.size() != n_row){
      cout << "pq.size() = " << pq.size() << " n_row " << k_max << endl;
      err("unexpected pq.size()");
    }
    */

    for0(i, k_max){
      f_i x(pq.top());
      size_t ki = (my_nxt_j * k_max) + i;
      dmat_d[ki] = x.f;
      dmat_i[ki] = x.i;
      // cprint(str("\t*i ") + to_string(my_nxt_j) + str(" j " ) + to_string(x.i) + str(" d " ) + to_string(dmat_d[ki])); // + str(" idx " ) + to_string(x.i));
      pq.pop();
    }

    while(pq.size() > 0) pq.pop();

    if(pq.size() > 0) err("failed to clear pq");
    //cout << "unlock" << endl;
  }
}

int main(int argc, char ** argv){

  if(argc < 2) err("csv_dmat [csv file]");

  size_t j, i;
  read_data(str(argv[1]));
  vector<str> fields(split(hdr));
  n_row = csv.size();
  n_col = fields.size();
  n_str = n_col * n_row;

  cout << "n_row " << n_row << endl;
  cout << "n_col " << n_col << endl;

  size_t k_max_default = 2222;
  k_max = ((n_row - 1) < k_max_default) ? (n_row - 1) : k_max_default;

  cout << "n_str " << n_str << endl;
  cout << "k_max: " << k_max << endl;

  int n_cores = sysconf(_SC_NPROCESSORS_ONLN);
  cout << "n_cores: " << n_cores << endl;

  // init memory for split strings
  dat = new str[n_str];

  if(!dat) err("failed to allocate memory");
  for0(j, n_str) dat[j] = str("");

  vector<str> words;
  for0(j, n_row){
    words = split(csv[j]);
    // cout << words << endl;
    for0(i, n_col){
      lower(words[i]);
      trim(words[i]);
      dat[j * n_col + i] = words[i];
    }
  }

  // allocate dmat
  dmat_d = (float *) alloc(n_row * k_max * sizeof(float));
  dmat_i = (size_t *) alloc(n_row * k_max * sizeof(size_t)); // meta

  cout << "fsize dmat.d " << n_row * k_max * sizeof(float) << endl;
  if(fsize("dmat.d") != n_row * k_max * sizeof(float)){
    // calculate the distance matrix
    nxt_j = 0;

    pthread_mutex_init(&print_mtx, NULL);
    pthread_mutex_init(&nxt_j_mtx, NULL);

    // make threads joinable
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

    pthread_t * my_pthread = new pthread_t[n_cores];
    for0(j, n_cores){
      pthread_create(&my_pthread[j], &attr, dmat_threadfun, (void *)j);
    }

    // must wait for all threads to exit
    for0(j, n_cores){
      pthread_join(my_pthread[j], NULL);
    }

    FILE * f;
    f = fopen("dmat.d", "wb");
    fwrite(dmat_d, n_row * k_max * sizeof(float), 1, f);
    fclose(f);
    f = fopen("dmat.i", "wb");
    fwrite(dmat_i, n_row * k_max * sizeof(size_t), 1, f);
    fclose(f);
  }
  else{
    // reload the distance matrix
  }

  return 0;
}
